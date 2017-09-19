function zip(collections) {
    let items = [];
    for (let i = 0; i < arguments[0].length; ++i) {
        let item = [];
        for (let collection of arguments) {
            item.push(collection[i]);
        }
        items.push(item);
    }
    return items;
}

export {
    zip
}