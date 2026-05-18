# Letters to copy: 𝜓 ç 𝜔


markdown_text = r"""
### Definition of Curves

- IS (Investments-Savings) curve:     
$$
Y = \omega - \phi r
$$
- MP (Monetary Policy) curve with $r' > 0, \lambda_P \ge 0, \lambda_I \ge 0$:    
$$
r = r' + \lambda_P \tilde{Y} + \lambda_I \pi 
$$
- IA (Inflation Adjustment) curve - horizontal line:
$$
\pi = const
$$
- AD (Aggregate Demand) curve - derived from IS and MP curves


### Coefficient Derivation

- IS:     
$$
Y = \omega - \phi r \\
\phi r = \omega -Y \\
r = \frac{\omega}{\phi} - \frac{1}{\phi} Y \\
r = \underbrace{\frac{\omega}{\phi}}_{\text{intercept}}
+ \underbrace{\left(-\frac{1}{\phi}\right)}_{\text{slope}} \cdot Y
$$

- MP:
$$
r = r' + \lambda_P \tilde{Y} + \lambda_I \pi \\
r = r' + \lambda_P \frac{(Y - \bar{Y})}{\bar{Y}} + \lambda_I \pi \\
r = r' + \frac{\lambda_P}{\bar{Y}} Y - \lambda_P + \lambda_I \pi \\
r = r' - \lambda_P + \lambda_I \pi  + \frac{\lambda_P}{\bar{Y}} Y  \\

r = \underbrace{\left(r' - \lambda_P + \lambda_I \pi\right)}_{\text{intercept}} + \underbrace{\left(\frac{\lambda_P}{\bar{Y}}\right)}_{\text{slope}} \cdot Y

$$  
- IA:
$$
\pi = const \\
\pi = \underbrace{\text{const}}_{\text{intercept}} 
+ \underbrace{0}_{\text{slope}} \cdot Y
$$

- AD - Derived from IS and MP curves as dependence  𝜋(Y):
$$
r_{IS} (Y) = r_{MP} (Y) \\
\frac{\omega}{\phi} - \frac{1}{\phi} Y = r' - \lambda_P + \lambda_I \pi  + \frac{\lambda_P}{\bar{Y}} Y  \\
\lambda_I \pi = - r' + \lambda_P  - \frac{\lambda_P}{\bar{Y}} Y + \frac{\omega}{\phi} - \frac{1}{\phi} Y \\
\pi = - \frac{r'}{\lambda_I} + \frac{\lambda_P}{\lambda_I} - \frac{\lambda_P}{\lambda_I \bar{Y}} Y
               + \frac{\omega}{\phi \lambda_I} - \frac{1}{\phi \lambda_I} Y \\
\pi = - \frac{r'}{\lambda_I} + \frac{\lambda_P}{\lambda_I} + \frac{\omega}{\phi \lambda_I} - \frac{\lambda_P}{\lambda_I \bar{Y}} Y - \frac{1}{\phi \lambda_I} Y \\
\pi = - \frac{r'}{\lambda_I} + \frac{\lambda_P}{\lambda_I} + \frac{\omega}{\phi \lambda_I} + (- \frac{\lambda_P}{\lambda_I \bar{Y}} - \frac{1}{\phi \lambda_I}) Y\\
\pi =\underbrace{\left(- \frac{r'}{\lambda_I} + \frac{\lambda_P}{\lambda_I} + \frac{\omega}{\phi \lambda_I}\right)}_{\text{intercept}} +
\underbrace{\left( - \frac{\lambda_P}{\lambda_I \bar{Y}} - \frac{1}{\phi \lambda_I}\right)}_{\text{slope}} \cdot Y
$$
"""


# r = r' + \lambda_P \tilde{Y} + \lambda_I \pi \text{ with } r' > 0, \lambda_P \ge 0, \lambda_I \ge 0.

tabs_options = ['📊 Time Model', '🏠 Home', '🧾 Glossary']  #'📊 Data'

standard_line_width = 3
thin_line_width = 2


Y_potential = 1
spead = 0.15

iteration_count = 30




neg_inflation_shock = """
<div style="text-align:center; font-size:17px; font-weight:700;">
    Negative Inflation Shock 📈
</div>

<div style="font-size:13px; color:gray;">
    Usually an external supply shock — a sudden increase in production costs or prices (e.g. the 1970s oil crisis). Inflation rises while output falls below potential.
    <br><br>
    In the short run, the central bank often raises interest rates to control inflation, making borrowing more expensive and reducing demand further. Over time, lower demand helps reduce inflation, and output gradually returns to its potential level.
</div>
"""

pos_monetary_shock = """
<div style="text-align:center; font-size:17px; font-weight:700;">
    Positive Monetary Shock 🏦
</div>

<div style="font-size:13px; color:gray;">
    An unexpected expansionary monetary policy shock — the central bank lowers nominal interest rates. Borrowing becomes cheaper, and in the short run the real interest rate also decreases. Investment and consumption increase, pushing output above potential.
    <br><br>
    In the long run, higher demand increases inflation, which gradually raises the real interest rate again and brings output back to the potential level.
</div>
"""

pos_demand_shock = """
<div style="text-align:center; font-size:17px; font-weight:700;">
    Positive Demand Shock 🛒
</div>

<div style="font-size:13px; color:gray;">
    A sudden increase in aggregate demand caused by higher consumption, investment, government spending, or exports.
    <br><br>
    In the short run, output rises above potential. As demand increases, inflation also rises. The central bank responds by increasing interest rates, slowing economic activity and gradually bringing output back to its potential level.
</div>
"""

placeholder_shock = """
<div style="
    height: 140px;
    display: flex;
    justify-content: center;
    align-items: center;
    text-align: center;
    font-size: 17px;
    color: #999999;
">
    Please Select a Shock
</div>
"""

# ---------- Fiscal Policy (omega) ----------
omega_text_exp = """
<div style="font-size:17px; font-weight:700; color:#222;">
    Positive Supply Shock 🏛️
</div>

<div style="font-size:13px; color:gray;">
    Either an external positive supply shock or a government increase in public spending or reduction in taxes.
</div>
"""

omega_text_res = """
<div style="font-size:17px; font-weight:700; color:#222;">
    Negative Supply Shock 🏛️
</div>

<div style="font-size:13px; color:gray;">
    Either a negative external event leading to an increase in world prices or a government reduction in aggregate demand through lower spending or higher taxes.
</div>
"""


# ---------- Monetary Policy (r) ----------
r_text_con = """
<div style="font-size:17px; font-weight:700; color:#222;">
    Contractionary Monetary Policy 💰
</div>

<div style="font-size:13px; color:gray;">
    The central bank raises interest rates and tightens financial conditions.
    Borrowing and investment decline, slowing inflation and aggregate demand.
</div>
"""

r_text_exp = """
<div style="font-size:17px; font-weight:700; color:#222;">
    Expansionary Monetary Policy 💰
</div>

<div style="font-size:13px; color:gray;">
    The central bank lowers interest rates and increases liquidity in the economy.
    Credit conditions improve, stimulating consumption, investment, and output.
</div>
"""


# ---------- Inflation Shock (pi) ----------
pi_text_inf = """
<div style="font-size:17px; font-weight:700; color:#222;">
    Inflationary Shock 📈
</div>

<div style="font-size:13px; color:gray;">
    A sudden increase in prices caused by supply disruptions, rising production costs,
    or commodity price increases. Inflation accelerates while real purchasing power declines.
</div>
"""

pi_text_def = """
<div style="font-size:17px; font-weight:700; color:#222;">
    Deflationary Shock 📉
</div>

<div style="font-size:13px; color:gray;">
    A decline in inflation or overall price levels caused by weak demand or falling costs.
    Economic activity may weaken as firms reduce production and investment.
</div>
"""




# \frac{\omega}{\phi} - \frac{1}{\phi} Y = r' - \lambda_P \bar{Y} + \lambda_I \pi + \lambda_P Y  \\
# \lambda_I \pi = - r' + \lambda_P \bar{Y}  - \lambda_P Y + \frac{\omega}{\phi} - \frac{1}{\phi} Y \\
# \pi = - \frac{r'}{\lambda_I} + \frac{\lambda_P}{\lambda_I}\bar{Y} - \frac{\lambda_P}{\lambda_I} Y
#               + \frac{\omega}{\phi \lambda_I} - \frac{1}{\phi \lambda_I} Y \ \
#  \
#     \pi = - \frac{r'}{\lambda_I} + \frac{\lambda_P}{\lambda_I}\bar{Y} + \frac{\omega}{\phi \lambda_I} - \frac{\lambda_P}{\lambda_I} Y - \frac{1}{\phi \lambda_I} Y \\
#
# \pi = - \frac{r'}{\lambda_I} + \frac{\lambda_P}{\lambda_I}\bar{Y}  + \frac{\omega}{\phi \lambda_I} + (- \frac{\lambda_P}{\lambda_I} - \frac{1}{\phi \lambda_I}) Y\\
#
#
# \pi =\underbrace{\left(- \frac{r'}{\lambda_I} + \frac{\lambda_P}{\lambda_I}\bar{Y} + \frac{\omega}{\phi \lambda_I}\right)}_{\text{intercept}} +
# \underbrace{\left( - \frac{\lambda_P}{\lambda_I} - \frac{1}{\phi \lambda_I}\right)}_{\text{slope}} \cdot Y
