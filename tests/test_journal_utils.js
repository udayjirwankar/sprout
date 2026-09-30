const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
vm.runInThisContext(fs.readFileSync('static/journal-utils.js', 'utf8'));
const helpers = globalThis.SproutJournal;
const entry = (date, id = 1, mood = 'good') => ({ created_at: date, entry_id: id, mood });
for (const timezone of ['Asia/Kolkata', 'America/New_York']) {
    process.env.TZ = timezone;
    const now = new Date(2026, 8, 30, 12);
    const datedEntry = (day, id = 1) => entry(new Date(2026, 8, day, 12).toISOString(), id);
    assert.equal(helpers.parseTimestamp('2026-09-30 00:30:00').toISOString(), '2026-09-30T00:30:00.000Z');
    assert.equal(helpers.currentStreak([], now), 0);
    assert.equal(helpers.currentStreak([datedEntry(30), datedEntry(29), datedEntry(28)], now), 3);
    assert.equal(helpers.currentStreak([datedEntry(30), datedEntry(30, 2), datedEntry(29)], now), 2);
    assert.equal(helpers.currentStreak([datedEntry(29), datedEntry(28)], now), 2);
    assert.equal(helpers.currentStreak([datedEntry(27), datedEntry(26)], now), 0);
    assert.equal(helpers.currentStreak([datedEntry(30), datedEntry(28)], now), 1);
    const fourteen = Array.from({ length: 14 }, (_, index) => datedEntry(17 + index));
    assert.equal(helpers.completedBlocks(fourteen, now), 2);
    assert.equal(helpers.completedBlocks([...fourteen, datedEntry(30, 9)], now), 2);
    const recent = helpers.recentDays([datedEntry(30), datedEntry(30, 2), datedEntry(28), datedEntry(20)], now);
    assert.equal(recent.length, 7);
    assert.equal(recent[6].entry.entry_id, 2);
    assert.equal(recent[5].entry, undefined);
    assert.equal(recent[4].entry.entry_id, 1);
    assert.equal(recent[0].entry, undefined);
    assert.equal(helpers.currentStreak([entry('invalid')], now), 0);
    // Calendar-day streaks must also work across the daylight-saving transition.
    const dstNow = new Date(2026, 2, 9, 12);
    const dstEntries = [7, 8, 9].map(day => entry(new Date(2026, 2, day, 12).toISOString()));
    assert.equal(helpers.currentStreak(dstEntries, dstNow), 3);
    console.log(`Calendar, streak, reward, and duplicate-day checks passed in ${timezone}.`);
}
for (const path of ['templates/index.html', 'templates/counselor.html']) {
    const source = fs.readFileSync(path, 'utf8');
    const scripts = [...source.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g)];
    for (const script of scripts) new vm.Script(script[1], { filename: path });
    console.log(`Inline JavaScript syntax checked in ${path}.`);
}
