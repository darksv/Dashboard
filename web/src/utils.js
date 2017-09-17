function clampArray(items, maxNumberOfItems) {
    return maxNumberOfItems > 0 && items.length > maxNumberOfItems
        ? items.slice(items.length - maxNumberOfItems)
        : items;
}

export {
    clampArray
}