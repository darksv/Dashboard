/*
    Converts shorthand symbols for time span into number of days,
    eg. 2w = 2 weeks = 2 * 7 days
 */
function convertShorthandIntoDays(shorthand: string): number {
    let periods = {
        'd': 1,
        'w': 7,
        'm': 30,
        'y': 365
    };

    let allowedSymbols = Object.keys(periods).join(''),
        regex = new RegExp('^(\\d+)([' + allowedSymbols + '])$'),
        match = regex.exec(shorthand);
    if (match === null) {
        return null;
    }

    let numberOfPeriods = parseInt(match[1]),
        periodType = match[2];

    return periods[periodType] * numberOfPeriods;
}

function addDaysTo(date: Date, days: number): Date {
    return new Date(date.getTime() + days * 24 * 3600 * 1000);
}

function shortenedDate(date: Date): string {
    return date.toISOString().substr(0, 10);
}

function isValidDate(string: string): boolean {
    return !isNaN(Date.parse(string));
}

export {
    convertShorthandIntoDays,
    addDaysTo,
    shortenedDate,
    isValidDate,
}