export class CommandController {

    /**
     * Parses raw code string into an Intermediate Representation (IR) by calling the backend.
     * @param {string} code - The source code from the editor.
     * @returns {Promise<Object>} IR - The structured intermediate representation.
     */
    static async parse(code) {
        try {
            // Debug: Log the exact URL being fetched
            const url = '/api/parse';
            console.log(`[CommandController] Fetching: ${new URL(url, window.location.origin).href}`);

            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ code }),
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error(`[CommandController] Error ${response.status}: ${response.statusText}`, errorText);
                throw new Error(`Network response was not ok: ${response.status} ${response.statusText} - ${errorText}`);
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
