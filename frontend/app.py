import os

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "https://linkanalysis-rgg6.onrender.com").rstrip("/")

st.set_page_config(page_title="AI Link Analysis", layout="wide")
st.title("AI Link Analysis")
st.caption("Competitors, search queries, SEO, services and audience for any website.")


def bullets(items):
    for item in items:
        st.markdown(f"- {item}")


url = st.text_input("Website URL", placeholder="https://example.com")

if st.button("Analyze", type="primary"):
    if not url.strip():
        st.warning("Enter a website URL.")
        st.stop()

    with st.spinner("Reading the website and analyzing it (can take 20-60 s)..."):
        try:
            resp = requests.post(f"{API_URL}/link-analysis", json={"url": url}, timeout=120)
        except requests.RequestException:
            st.error("Could not reach the API. Is it running?")
            st.stop()

    try:
        body = resp.json()
    except ValueError:
        st.error(f"Unexpected response from the API (HTTP {resp.status_code}).")
        st.stop()

    if not resp.ok or not body.get("success"):
        err = body.get("error", {})
        st.error(f"{err.get('code', 'ERROR')}: {err.get('message', 'Something went wrong.')}")
        st.stop()

    brand, analysis = body["brand"], body["analysis"]

    st.subheader(brand["name"])
    st.caption(f"{brand['category']} | {body['website']}")
    st.write(brand["summary"])

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Competitors", "Search queries", "SEO", "Services", "Audience"]
    )

    with tab1:
        comp = analysis["competitor_analysis"]
        st.write(comp["brand_overview"])
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Your strengths**")
            bullets(comp["strengths"])
        with c2:
            st.markdown("**Opportunities**")
            bullets(comp["opportunities"])
        st.markdown("**Competitors**")
        st.dataframe(comp["competitors"], use_container_width=True, hide_index=True)
        st.caption(comp["note"])

    with tab2:
        st.dataframe(analysis["target_search_queries"], use_container_width=True, hide_index=True)

    with tab3:
        seo = analysis["seo_improvements"]
        st.markdown(f"**Primary keyword:** {seo['primary_keyword']}")
        st.markdown("**Secondary / long-tail keywords**")
        bullets(seo["secondary_keywords"])
        st.markdown(f"**Recommended title** ({len(seo['recommended_title'])} chars)")
        st.code(seo["recommended_title"], language=None)
        st.markdown(f"**Meta description** ({len(seo['meta_description'])} chars)")
        st.code(seo["meta_description"], language=None)
        st.markdown("**Supporting content ideas**")
        bullets(seo["supporting_content"])

    with tab4:
        st.dataframe(analysis["top_services"], use_container_width=True, hide_index=True)
        st.caption('"inferred" means the service was not stated on the website.')

    with tab5:
        aud = analysis["target_audience"]
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Primary audience**")
            bullets(aud["primary_audience"])
            st.markdown("**Industries**")
            bullets(aud["industries"])
        with c2:
            st.markdown("**Secondary audience**")
            bullets(aud["secondary_audience"])
            st.markdown("**Customer needs**")
            bullets(aud["customer_needs"])

    with st.expander("Raw JSON"):
        st.json(body)
