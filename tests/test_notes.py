from lorestitch.core.notes import extract_links_and_tags
def test_extract_links_and_tags():
    s = "Hello [[World Note]] and #tag1 #tag2."
    meta = extract_links_and_tags(s)
    assert "World Note" in meta["links"]
    assert "tag1" in meta["tags"] and "tag2" in meta["tags"]
