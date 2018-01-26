function zip<T>(...collections: Array<T>): Array<Array<T>> {
    let items = [];
    for (let i = 0; i < arguments[0].length; ++i) {
        let item = [];
        for (let collection of collections) {
            item.push(collection[i]);
        }
        items.push(item);
    }
    return items;
}

export {
    zip
}