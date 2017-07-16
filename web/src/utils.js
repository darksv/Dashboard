module.exports =  {
    clampArray: function(items, maxNumberOfItems) {
        return maxNumberOfItems > 0 && items.length > maxNumberOfItems
            ? items.slice(items.length - maxNumberOfItems)
            : items;
    }
}