import streamlit as st
from store import get_all_urls, get_all_keywords, store_url, store_keyword
from db import get_connection


def _delete_url(url):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM searched_urls WHERE url = %s", (url,))
        conn.commit()


def _delete_keyword(keyword):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM searched_keywords WHERE keyword = %s", (keyword,))
        conn.commit()


def render():
    st.header("Manage URLs & Keywords")
    col_urls, col_kws = st.columns(2)

    with col_urls:
        st.subheader("Stored URLs")
        urls = get_all_urls()
        st.caption(f"{len(urls)} stored")

        new_url = st.text_input("Add URL:", placeholder="https://example.com/planning/")
        if st.button("Add URL"):
            if new_url.strip().startswith(("http://", "https://")):
                store_url(new_url.strip())
                st.success(f"Added: {new_url.strip()}")
                st.rerun()
            else:
                st.error("Must start with http:// or https://")

        st.divider()
        for i, url in enumerate(urls):
            c1, c2 = st.columns([5, 1])
            c1.write(url)
            if c2.button("Delete", key=f"del_url_{i}"):
                _delete_url(url)
                st.rerun()

    with col_kws:
        st.subheader("Stored Keywords")
        keywords = get_all_keywords()
        st.caption(f"{len(keywords)} stored")

        new_kw = st.text_input("Add keyword:", placeholder="solar panel")
        if st.button("Add Keyword"):
            if new_kw.strip():
                store_keyword(new_kw.strip())
                st.success(f"Added: {new_kw.strip().lower()}")
                st.rerun()
            else:
                st.error("Keyword cannot be empty")

        st.divider()
        for i, kw in enumerate(keywords):
            c1, c2 = st.columns([5, 1])
            c1.write(kw)
            if c2.button("Delete", key=f"del_kw_{i}"):
                _delete_keyword(kw)
                st.rerun()
