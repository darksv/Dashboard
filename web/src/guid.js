function generateGuid() {
    var result = '';
    for (var j = 0; j < 32; j++) {
        if (j in [8, 12, 16, 20])
            result += '-';
        result += Math.floor(Math.random() * 16).toString(16).toUpperCase();
    }
    return result;
}

export default {
    generate: generateGuid
};