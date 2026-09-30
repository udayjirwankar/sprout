/* SQLite dates are UTC. Group check-ins by the student's local calendar day. */
(() => {
    function parseTimestamp(value) {
        if (typeof value !== 'string') return new Date(NaN);
        const normalized = value.replace(' ', 'T');
        return new Date(/[zZ]$|[+-]\d{2}:?\d{2}$/.test(normalized)
            ? normalized : normalized + 'Z');
    }

    function dayKey(date) {
        return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
    }

    function dayNumber(date) {
        // Compare calendar dates without daylight-saving hour differences.
        return Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()) / 86400000;
    }

    function journalDays(entries, now = new Date()) {
        const today = dayNumber(now);
        return [...new Set(entries.map(entry => dayNumber(parseTimestamp(entry.created_at)))
            .filter(day => Number.isFinite(day) && day <= today))].sort((a, b) => a - b);
    }

    function currentStreak(entries, now = new Date()) {
        const days = journalDays(entries, now);
        if (!days.length || dayNumber(now) - days.at(-1) > 1) return 0;
        let streak = 1;
        for (let index = days.length - 1; index > 0; index--) {
            if (days[index] - days[index - 1] !== 1) break;
            streak++;
        }
        return streak;
    }

    function completedBlocks(entries, now = new Date()) {
        const days = journalDays(entries, now);
        if (!days.length) return 0;
        let total = 0;
        let run = 1;
        for (let index = 1; index < days.length; index++) {
            if (days[index] - days[index - 1] === 1) run++;
            else { total += Math.floor(run / 7); run = 1; }
        }
        return total + Math.floor(run / 7);
    }

    function recentDays(entries, now = new Date()) {
        const latest = new Map();
        for (const entry of entries) {
            const date = parseTimestamp(entry.created_at);
            if (Number.isNaN(date.getTime())) continue;
            const key = dayKey(date);
            const previous = latest.get(key);
            if (!previous || date > parseTimestamp(previous.created_at) ||
                (date.getTime() === parseTimestamp(previous.created_at).getTime() && entry.entry_id > previous.entry_id)) {
                latest.set(key, entry);
            }
        }
        return Array.from({ length: 7 }, (_, index) => {
            const date = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 6 + index);
            return { date, entry: latest.get(dayKey(date)) };
        });
    }

    globalThis.SproutJournal = { parseTimestamp, currentStreak, completedBlocks, recentDays };
})();
