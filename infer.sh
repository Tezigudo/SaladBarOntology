#!/bin/bash

# Find all scripts matching the pattern
scripts=(scripts/for_inferred_property/hasTotal*.py)

# Check if there are any scripts to run
if [ ${#scripts[@]} -eq 0 ]; then
    echo "No scripts found matching the pattern 'scripts/for_inferred_property/hasTotal*.py'."
    exit 1
fi

# Initialize arrays to track successful and failed scripts
successful_scripts=()
failed_scripts=()

for script in "${scripts[@]}"; do
    echo "======================================="
    echo "Running $script..."
    echo "======================================="
    python "$script"
    exit_status=$?
    echo "======================================="
    if [ $exit_status -eq 0 ]; then
        echo "$script completed successfully."
        successful_scripts+=("$script")
    else
        echo "$script failed with exit status $exit_status."
        failed_scripts+=("$script")
    fi
    echo "======================================="
    echo
done

# Final summary
echo "All scripts have been run."
echo "Total scripts: ${#scripts[@]}"
echo "Successful: ${#successful_scripts[@]}"
echo "Failed: ${#failed_scripts[@]}"
echo

if [ ${#successful_scripts[@]} -gt 0 ]; then
    echo "Successful scripts:"
    for s in "${successful_scripts[@]}"; do
        echo "- $s"
    done
else
    echo "No successful scripts."
fi
echo

if [ ${#failed_scripts[@]} -gt 0 ]; then
    echo "Failed scripts:"
    for f in "${failed_scripts[@]}"; do
        echo "- $f"
    done
else
    echo "No failed scripts."
fi