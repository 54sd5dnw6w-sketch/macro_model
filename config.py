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
r = r' + \lambda_P (Y - \bar{Y}) + \lambda_I \pi \\
r = r' + \lambda_P Y - \lambda_P \bar{Y} + \lambda_I \pi \\
r = r' - \lambda_P \bar{Y} + \lambda_I \pi + \lambda_P Y  \\
r = \underbrace{\left( r' - \lambda_P \bar{Y} + \lambda_I \pi \right)}_{\text{intercept}}
+ \underbrace{\lambda_P}_{\text{slope}} \cdot Y
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
\frac{\omega}{\phi} - \frac{1}{\phi} Y = r' - \lambda_P \bar{Y} + \lambda_I \pi + \lambda_P Y  \\
\lambda_I \pi = - r' + \lambda_P \bar{Y}  - \lambda_P Y + \frac{\omega}{\phi} - \frac{1}{\phi} Y \\

\pi = - \frac{r'}{\lambda_I} + \frac{\lambda_P}{\lambda_I}\bar{Y} - \frac{\lambda_P}{\lambda_I} Y
+ \frac{\omega}{\phi \lambda_I} - \frac{1}{\phi \lambda_I} Y \\

\pi = - \frac{r'}{\lambda_I} + \frac{\lambda_P}{\lambda_I}\bar{Y} + \frac{\omega}{\phi \lambda_I} - \frac{\lambda_P}{\lambda_I} Y - \frac{1}{\phi \lambda_I} Y \\

\pi = - \frac{r'}{\lambda_I} + \frac{\lambda_P}{\lambda_I}\bar{Y}  + \frac{\omega}{\phi \lambda_I} + (- \frac{\lambda_P}{\lambda_I} - \frac{1}{\phi \lambda_I}) Y\\


\pi =\underbrace{\left(- \frac{r'}{\lambda_I} + \frac{\lambda_P}{\lambda_I}\bar{Y} + \frac{\omega}{\phi \lambda_I}\right)}_{\text{intercept}} +
\underbrace{\left( - \frac{\lambda_P}{\lambda_I} - \frac{1}{\phi \lambda_I}\right)}_{\text{slope}} \cdot Y

$$
"""


# r = r' + \lambda_P \tilde{Y} + \lambda_I \pi \text{ with } r' > 0, \lambda_P \ge 0, \lambda_I \ge 0.

tabs_options = ['🏠 Home', '🧾 Glossary']  #'📊 Data'

standard_line_width = 3
thin_line_width = 2

# "solid"
# "dot"
# "dash"
# "longdash"
# "dashdot"
# "longdashdot"
# '5px,2px'