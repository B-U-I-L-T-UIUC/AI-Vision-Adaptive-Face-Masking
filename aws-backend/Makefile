LAMBDA_DIR=lambda_api
PACKAGE_DIR=$(LAMBDA_DIR)/packages
ZIP_FILE=$(LAMBDA_DIR)/function.zip

.PHONY: clean zip deploy

# Remove old zip file and cleanup packages
clean:
	rm -f $(ZIP_FILE)
	rm -rf $(PACKAGE_DIR)
	rm -rf $(LAMBDA_DIR)/__pycache__

# Install dependencies in a separate "packages" folder
zip: clean
	mkdir -p $(PACKAGE_DIR)
	pip install -r $(LAMBDA_DIR)/requirements.txt -t $(PACKAGE_DIR)
	cd $(PACKAGE_DIR) && zip -r ../function.zip .
	cd $(LAMBDA_DIR) && zip -g function.zip main.py
	rm -rf $(PACKAGE_DIR)  # Remove packages folder after zipping

# Deploy using Terraform
deploy: zip
	terraform init
	terraform apply -auto-approve
