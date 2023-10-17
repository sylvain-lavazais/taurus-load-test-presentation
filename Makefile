
##  ------------
##@ Presentation
##  ------------

presentation: ## Start the presentation web server
	@echo "===> $@ <==="
	@docker run --rm -p 1948:1948 -p 35729:35729 -v $(shell pwd)/presentation:/slides webpronl/reveal-md:latest /slides --watch --css style/custom.css --highlight-theme github-dark
.PHONY: presentation

presentation-w-notes: .clean-presentation .prepare-print ## Start the presentation web server (with notes)
	@echo "===> $@ <==="
	@docker run -d -p 1948:1948 -p 35729:35729 -v $(shell pwd)/presentation:/slides --name reveal-md webpronl/reveal-md:latest /slides --css style/custom.css --highlight-theme github-dark
	@sh ./tools/print-mode.sh
	@$(MAKE) .clean-presentation
.PHONY: presentation-w-notes

export-pdf: .clean-presentation .prepare-print ## Export presentation to pdf (used in GH action)
	@echo "===> $@ <==="
	@docker run -d -p 1948:1948 -v $(shell pwd)/presentation:/slides --name reveal-md webpronl/reveal-md:latest /slides --css style/custom.css --highlight-theme github-dark
	@mkdir generation_tmp && chmod 777 generation_tmp
	@sleep 5
	@sh ./tools/print-pdf.sh
	@$(MAKE) .clean-presentation
.PHONY: export-pdf

.prepare-print:
	@echo "===> $@ <==="
	@cp presentation/style/print-options.json presentation/reveal.json
.PHONY: .prepare-print

.clean-presentation:
	@echo "===> $@ <==="
	@docker stop reveal-md || true
	@docker rm reveal-md || true
	@rm -rf generation_tmp || true
	@rm -rf presentation/reveal.json || true
.PHONY: .clean-presentation

##  ----
##@ Demo
##  ----

## TODO

##  ----
##@ Misc
##  ----

prepare-release: ## Prepare files before making a new release of version
	@echo "===> $@ <==="
	@sed -Ei 's/version = .*/version = "${VERSION}"/g' demo/pyproject.toml
.PHONY: prepare-release

.DEFAULT_GOAL := help
APPLICATION_TITLE := Presentation : Load tests with Blazemeters Taurus \n =================================================
.PHONY: help
help: ## Display this help
	@awk 'BEGIN {FS = ":.* ##"; printf "\n\033[32;1m ${APPLICATION_TITLE}\033[0m\n\n\033[1mUsage:\033[0m\n'\
'  \033[31mmake \033[36m<option>\033[0m\n"} /^[%a-zA-Z_-]+:.* ## / { printf "  \033[33m%-25s\033[0m %s\n", $$1, $$2 }'\
' /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' ${MAKEFILE_LIST}

##@
