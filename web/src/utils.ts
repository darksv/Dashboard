function clampArray<T>(items: Array<T>, maxNumberOfItems: number): Array<T> {
    return maxNumberOfItems > 0 && items.length > maxNumberOfItems
        ? items.slice(items.length - maxNumberOfItems)
        : items;
}

export {
    clampArray
}