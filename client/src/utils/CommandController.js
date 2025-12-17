export class CommandController {

    /**
     * Parses raw code string into an Intermediate Representation (IR) by calling the backend.
     * @param {string} code - The source code from the editor.
     * @returns {Promise<Object>} IR - The structured intermediate representation.
     */
    static async parse(code) {
        try {
            const response = await fetch('http://127.0.0.1:5000/parse', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ code }),
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();

            // Ensure default structure if backend returns minimal data
            return {
                structures: data.structures || [],
                hasLoop: data.hasLoop || false,
                loopTarget: data.target || null,
                loopIterator: data.iterator || null,
                loopDependencies: data.loopDependencies || []
            };
        } catch (error) {
            console.error("Parsing error:", error);
            // Return empty structure on error to prevent app crash
            return { structures: [], hasLoop: false, target: null, iterator: null, loopDependencies: [] };
        }
    }
}
