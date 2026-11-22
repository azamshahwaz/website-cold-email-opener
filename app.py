"""Website to AI Cold Email Opener — Streamlit app."""
from __future__ import annotations

import html
import json
import time
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from config import load_settings
from modules.demo import DEMO_LABEL, DEMO_SAMPLE_NAMES, get_demo_result
from modules.errors import AppError
from modules.pipeline import OpenerPipeline, PipelineResult
from modules.utils import estimate_cost_usd, setup_logging

logger = setup_logging()
ASSETS_DIR = Path(__file__).parent / "assets"

st.set_page_config(page_title="Website to AI Cold Email Opener", page_icon="✉️", layout="centered")


@st.cache_resource
def get_pipeline() -> OpenerPipeline:
    return OpenerPipeline(load_settings())


settings = load_settings()
esc = html.escape


def inject_css() -> None:
    css_path = ASSETS_DIR / "custom.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def card(title: str, body_html: str) -> None:
    st.markdown(f'<div class="card"><div class="card-label">{esc(title)}</div>{body_html}</div>',
                unsafe_allow_html=True)


def copy_button(text: str) -> None:
    payload = json.dumps(text).replace("</", "<\\/")
    components.html(
        f"""<style>
        body{{margin:0;font-family:-apple-system,Segoe UI,Roboto,sans-serif}}
        button{{width:100%;height:40px;border:1px solid #cbd5e1;border-radius:8px;background:#fff;
        color:#0f172a;font-size:14px;cursor:pointer}} button:hover{{background:#f1f5f9}}
        </style><button id="b">Copy Opener</button>
        <script>
        const text={payload}; const b=document.getElementById('b');
        b.onclick=async()=>{{
          try{{await navigator.clipboard.writeText(text);}}
          catch(e){{const a=document.createElement('textarea');a.value=text;document.body.appendChild(a);
          a.select();document.execCommand('copy');a.remove();}}
          b.textContent='Copied ✓'; setTimeout(()=>b.textContent='Copy Opener',1600);
        }};
        </script>""",
        height=44,
    )


def clear_state() -> None:
    st.session_state.update(result=None, error=None, url_input="")


def run_generation(force_regenerate: bool = False) -> None:
    st.session_state.error = None
    demo = st.session_state.demo_mode
    started = time.perf_counter()
    raw_url = st.session_state.result["input_url"] if force_regenerate and st.session_state.get("result") \
        else st.session_state.get("url_input", "")
    with st.status("Working on it…", expanded=True) as status:
        try:
            if demo:
                sample = st.session_state.demo_sample
                status.write("• Loading sample website data (demo mode, no network or AI call)")
                website, opener = get_demo_result(sample)
                result = PipelineResult(website, opener)
                raw_url = sample
            else:
                result = get_pipeline().run(raw_url, on_step=lambda msg: status.write(f"• {msg}…"),
                                            force_regenerate=force_regenerate)
            st.session_state.result = {"data": result, "demo": demo, "input_url": raw_url,
                                       "seconds": time.perf_counter() - started}
            status.update(label="Done", state="complete", expanded=False)
        except AppError as exc:
            st.session_state.error, st.session_state.result = exc.user_message, None
            status.update(label="Could not generate an opener", state="error", expanded=False)
        except Exception:  # never show raw stack traces to users
            logger.exception("Unexpected error while generating opener")
            st.session_state.error = "An unexpected error occurred. Please try again."
            st.session_state.result = None
            status.update(label="Unexpected error", state="error", expanded=False)


def render_result(stored: dict) -> None:
    result: PipelineResult = stored["data"]
    website, opener = result.website, result.opener
    is_demo = stored["demo"]

    card("Company Website", f'<a href="{esc(website.final_url)}" target="_blank" rel="noopener noreferrer">'
                            f'{esc(website.final_url)}</a>' + (f'<div class="muted">{esc(website.title)}</div>' if website.title else ""))
    card("Company Description", f"<p>{esc(website.description)}</p>")
    headings = "".join(f"<li>{esc(h)}</li>" for h in website.headings[:8])
    excerpt = website.main_text[:700] + ("…" if len(website.main_text) > 700 else "")
    with st.expander("Extracted Website Content Summary", expanded=False):
        st.markdown(
            f'<div class="muted">{len(website.main_text):,} characters of page text extracted'
            f'{" (demo sample)" if is_demo else ""}.</div>'
            + (f"<strong>Key headings</strong><ul>{headings}</ul>" if headings else "")
            + f'<strong>Text excerpt</strong><p class="excerpt">{esc(excerpt)}</p>',
            unsafe_allow_html=True)

    lines_html = "".join(
        f'<div class="opener-line"><span class="badge">{i}</span><span>{esc(line)}</span></div>'
        for i, line in enumerate(opener.lines, 1))
    banner = f'<div class="demo-banner">{esc(DEMO_LABEL)}</div>' if is_demo else ""
    st.markdown(f'<div class="card opener-card"><div class="card-label">Generated Opener</div>'
                f'{banner}{lines_html}</div>', unsafe_allow_html=True)

    if is_demo:
        st.caption("Demo mode · pre-written sample, no AI call made.")
    else:
        cost = estimate_cost_usd(opener.input_tokens, opener.output_tokens,
                                 settings.price_input_per_1m, settings.price_output_per_1m)
        origin = "from cache" if result.opener_from_cache else f"{stored['seconds']:.1f}s"
        st.caption(f"Model {opener.model} · {opener.input_tokens:,} input / {opener.output_tokens:,} output tokens "
                   f"· est. ${cost:.5f} at configured prices · {origin}")

    col_copy, col_again, col_clear = st.columns(3)
    with col_copy:
        copy_button("\n".join(opener.lines))
    with col_again:
        again = st.button("Generate Again", use_container_width=True, key="again_btn")
    with col_clear:
        st.button("Clear", use_container_width=True, key="clear_btn", on_click=clear_state)
    with st.expander("Plain text (select and copy)"):
        st.code("\n".join(opener.lines), language=None)
    if again:
        run_generation(force_regenerate=not is_demo)
        st.rerun()


def sidebar() -> None:
    with st.sidebar:
        st.header("Settings")
        st.toggle("Demo mode (no API key needed)", key="demo_mode",
                  help="Uses fictional sample websites and pre-written openers. Nothing is sent to an AI model.")
        if st.session_state.demo_mode:
            st.info("Demo mode is on. Output is pre-written and clearly labelled.")
        elif settings.has_api_key:
            st.success(f"Gemini API key configured\n\nModel: `{settings.model}`")
        else:
            st.warning("No GEMINI_API_KEY found. Add it to `.env` or turn on Demo mode.")
        with st.expander("Cost estimator"):
            in_tok = st.number_input("Input tokens / request", 100, 100_000, 2300, step=100)
            out_tok = st.number_input("Output tokens / request", 10, 5_000, 150, step=10)
            p_in = st.number_input("Input price (USD / 1M tokens)", 0.0, 100.0, float(settings.price_input_per_1m))
            p_out = st.number_input("Output price (USD / 1M tokens)", 0.0, 100.0, float(settings.price_output_per_1m))
            per_day = st.number_input("Requests / day", 1, 1_000_000, 1000, step=100)
            per_request = estimate_cost_usd(in_tok, out_tok, p_in, p_out)
            st.metric("Cost / request", f"${per_request:.5f}")
            st.metric("Cost / day", f"${per_request * per_day:,.2f}")
            st.metric("Cost / 30 days", f"${per_request * per_day * 30:,.2f}")
            st.caption("Check the provider's official pricing page for current prices. Free-tier quotas may apply.")


def main() -> None:
    inject_css()
    st.session_state.setdefault("demo_mode", not settings.has_api_key)
    st.session_state.setdefault("result", None)
    st.session_state.setdefault("error", None)
    sidebar()

    st.markdown('<h1 class="app-title">Website to AI Cold Email Opener</h1>'
                '<p class="app-subtitle">Generate personalized, website-grounded three-line openers for founder outreach.</p>',
                unsafe_allow_html=True)

    if st.session_state.demo_mode:
        st.selectbox("Choose a sample company (fictional)", DEMO_SAMPLE_NAMES, key="demo_sample")
    else:
        st.text_input("Enter company website URL", placeholder="https://company.com", key="url_input")

    col_go, col_clear, _ = st.columns([2, 1, 3])
    with col_go:
        generate = st.button("Generate Opener", type="primary", use_container_width=True, key="generate_btn")
    with col_clear:
        if st.session_state.result is None:
            st.button("Clear", use_container_width=True, key="clear_top_btn", on_click=clear_state)

    if generate:
        run_generation()
    if st.session_state.error:
        st.error(st.session_state.error)
    if st.session_state.result:
        render_result(st.session_state.result)

    st.markdown('<p class="footer">Always review an opener before sending it. Openers are grounded in the '
                'public text of the page you submit, which may be incomplete.</p>', unsafe_allow_html=True)


main()
