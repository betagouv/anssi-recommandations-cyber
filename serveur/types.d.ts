export type ReponseAPIAlbert = {
    data: {
        score: number;
        chunk: {
            metadata: {
                document_name: string;
            },
            content: string
        }
    }[]
}