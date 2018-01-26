class PageTitleChanger {
    private originalTitle: string = null;

    constructor() {
        this.originalTitle = document.title;
    }

    public setPrefix(prefix: string) {
        document.title = prefix + this.originalTitle;
    }

    public clearPrefix() {
        document.title = this.originalTitle;
    }
}

export {
    PageTitleChanger
};