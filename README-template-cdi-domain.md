# 🧪 CDI Domain Template

This is the official **template repository** for all **Complex Data Insights (CDI)** domain guides.  
It provides a consistent, layered Bookdown structure in **R and Python**, ready for real-world data science applications.

📘 **Use this template** to create your own domain-specific guide with a modular, reproducible setup.

---

## 📦 Features

- ✅ Modular Bookdown structure with four core layers:
  - Exploratory Data Analysis (**EDA**)
  - Visualization (**VIZ**)
  - Statistical Analysis (**STATS**)
  - Machine Learning (**ML**)
- ✅ Preconfigured for both **GitBook** and **PDF** output
- ✅ Built-in R/Python environment setup scripts
- ✅ Clear folder structure with automation-ready scripts
- ✅ Includes `.gitignore`, metadata, and default configuration files

---

## 🚀 How to Use This Template

1. Click **"Use this template"** on GitHub.
2. Clone your newly created repository:
   ```bash
   git clone https://github.com/your-org/your-new-domain.git
   cd your-new-domain
   ```
3. Make the setup scripts executable:
   ```bash
   chmod +x scripts/setup_r_env.sh
   chmod +x scripts/setup_py_env.sh
   ```
4. Set up your environments:
   ```bash
   ./scripts/setup_r_env.sh
   ./scripts/setup_py_env.sh
   ```
5. Build the full Bookdown guide:
   ```bash
   ./scripts/build-all.sh
   ```

---

## 📁 Folder Overview

```text
data/              → Sample dataset (e.g., iris.csv)
images/            → Cover image (must be images/cover.png)
library/           → CSL + BibTeX files
scripts/           → R/Python setup scripts
*.ipynb            → Q&A entries (one at a time)
*.Rmd              → Q&A entries (one at a time)
_bookdown-*.yml    → Layer-specific file list for Bookdown (e.g., EDA, VIZ, STATS, ML)
index-*.Rmd        → Entry points for Bookdown build (GitBook or PDF, per layer)
_output.yml        → Output configuration (GitBook and/or PDF settings)
```

---

## 📝 Template Instructions

- 🧩 **Replace this `README.md`** with your domain-specific version once the content is added.
- 🛡️ **Keep the `LICENSE`, output config, and helper scripts** — they apply to all CDI domain repos.
- 🛠️ Rename `scripts/domain.R` if needed to reflect your domain (e.g., `rna.R`, `gwas.R`).
- 🧪 Begin adding your real Q&A entries to `.Rmd` or `.ipynb` files in the appropriate layer.

---

## 📄 License

All source code in this repository is licensed under the [MIT License](LICENSE).  
All educational content (Q&A, explanations, markdown) is shared under the [CC BY 4.0 License](https://creativecommons.org/licenses/by/4.0/).  
Attribution is appreciated in derivative works, training programs, or redistributed materials.

---

## 👥 Maintainers

Created and maintained by the **CDI Team** at [ComplexDataInsights.com](https://complexdatainsights.com)
