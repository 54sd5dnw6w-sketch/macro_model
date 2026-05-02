import streamlit as st

HTML = """
<div style="font-size:18px;">
  y =
  <input id="a" type="number" class="coef"> * x +
  <input id="b" type="number" class="coef">
</div>
"""

# HTML = """
# <div style="font-size:18px;">
#   y =
#   <span>a</span>
#   <input id="a" type="number" value="1" class="coef"> * x +
#   <span>b</span>
#   <input id="b" type="number" value="0" class="coef">
# </div>
# """


JS = """
export default function(component) {
    const { setTriggerValue, parentElement } = component;

    const aInput = parentElement.querySelector("#a");
    const bInput = parentElement.querySelector("#b");

    const sendValue = () => {
        const a = parseFloat(aInput.value);
        const b = parseFloat(bInput.value);

        setTriggerValue("change", { a, b });
    };

    aInput.addEventListener("input", sendValue);
    bInput.addEventListener("input", sendValue);

    // initial value
    sendValue();
}
"""

CSS = """
.coef {
    width: 50px;
    border: none;
    border-bottom: 1px solid var(--st-border-color);
    text-align: center;
    font-size: 16px;
    background: transparent;
}

.coef:focus {
    outline: none;
    border-bottom: 1px solid var(--st-primary-color);
}
"""

linear_component = st.components.v2.component(
    "linear_input_inline",
    html=HTML,
    css=CSS,
    js=JS,
)

#result = linear_component(on_change_change=lambda: None)

result = linear_component()

a = 1.0
b = 0.0

if isinstance(result, dict):
    a = result.get("a", a)
    b = result.get("b", b)

st.write(a)
st.write(b)