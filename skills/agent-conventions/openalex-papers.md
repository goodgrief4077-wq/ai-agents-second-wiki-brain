# Papers and books: OpenAlex

For academic papers, open-access PDFs and books, use the OpenAlex API at `api.openalex.org`.

## Rules
1. The API key lives in the user's environment variable `OPENALEX_API_KEY`. Never write the key into a file, a note or a commit.
2. Send it as the header `Authorization: Bearer $OPENALEX_API_KEY`, or as `?api_key=`.
3. Never put the user's email address in requests.
4. Match titles with `filter=title.search:<phrase>`. Full-text `search=` returns off-topic hits.
5. Add `open_access.is_oa:true` when the user wants a readable PDF, and sort with `sort=cited_by_count:desc`.
6. Verify every download starts with `%PDF-` before trusting it.

Agent guide from the provider: https://help.openalex.org/api/llm-quick-reference
