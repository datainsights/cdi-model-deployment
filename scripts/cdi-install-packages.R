# 📦 CDI Modular Package Installer (scripts/cdi-install-packages.R)

# Load shared R packages
source("scripts/common.R")

# Detect target domain from environment variable (default to "general")
domain <- Sys.getenv("CDI_DOMAIN", unset = "general")
message("🔍 Target domain: ", domain)

# Construct path to domain-specific package script
domain_file <- file.path("scripts", paste0(domain, ".R"))

# Source domain-specific packages if the file exists
if (file.exists(domain_file)) {
  source(domain_file)
} else {
  message("⚠️ No domain-specific packages loaded for domain: ", domain)
}

# Snapshot the current environment (if renv is available)
if (requireNamespace("renv", quietly = TRUE)) {
  message("📦 Snapshotting renv environment...")
  renv::snapshot()
} else {
  warning("❌ renv is not installed. Skipping snapshot.")
}