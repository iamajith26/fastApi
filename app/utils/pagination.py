from typing import List, Any

def paginate(query: List[Any], page: int = 1, page_size: int = 10) -> dict:
    total_items = len(query)
    total_pages = (total_items + page_size - 1) // page_size
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    items = query[start_index:end_index]

    return {
        "page": page,
        "page_size": page_size,
        "total_items": total_items,
        "total_pages": total_pages,
        "items": items,
    }