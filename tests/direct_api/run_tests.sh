#!/bin/bash
# Run direct API tests for UNHCR IATI MCP Server

echo "========================================================================"
echo "UNHCR IATI MCP - Direct API Tests"
echo "========================================================================"
echo ""

# Check if we're in the right directory
if [ ! -f "test_api_calls.py" ]; then
    echo "Error: Please run this script from tests/direct_api/"
    exit 1
fi

# Create results directory if it doesn't exist
mkdir -p results

# Run the tests
echo "Starting tests..."
echo "Results will be saved to: $(pwd)/results/"
echo ""

python -m tests.direct_api.test_api_calls

# Show results
echo ""
echo "========================================================================"
echo "Test Results Summary"
echo "========================================================================"
echo ""

RESULT_COUNT=$(ls -1 results/*.json 2>/dev/null | wc -l)
if [ "$RESULT_COUNT" -gt 0 ]; then
    echo "✅ Tests completed successfully!"
    echo ""
    echo "Number of result files: $RESULT_COUNT"
    echo ""
    echo "Result files:"
    ls -1h results/*.json | head -20
    echo ""
    echo "To view all results:"
    echo "  ls -lh results/"
    echo ""
    echo "To clean up results:"
    echo "  rm -rf results/*"
else
    echo "⚠️  No result files found. Tests may have failed."
fi

echo ""
echo "========================================================================"
