#!/bin/bash

# Django FBF Project Rebuild Script
# This script stops the project, runs all tests, and restarts if tests pass

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/Users/maximilianfischer/git/django_fbf"
TEST_DIR="$PROJECT_DIR/test"
APP_DIR="$PROJECT_DIR/app"
DOCKER_COMPOSE_FILE="$PROJECT_DIR/docker-compose.yaml"
DOCKER_COMPOSE_PROD_FILE="$PROJECT_DIR/docker-compose.prod.yml"

# Logging
LOG_FILE="$PROJECT_DIR/rebuild_$(date +%Y%m%d_%H%M%S).log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    log_info "Docker is running"
}

# Function to stop the project
stop_project() {
    log_info "Stopping Django FBF project..."
    
    cd "$PROJECT_DIR"
    
    # Stop using existing stop script if available
    if [ -f "./stop_project.sh" ]; then
        log_info "Using existing stop_project.sh script"
        ./stop_project.sh 2>&1 | tee -a "$LOG_FILE"
    else
        # Stop using docker-compose
        if [ -f "$DOCKER_COMPOSE_FILE" ]; then
            log_info "Stopping containers using docker-compose"
            docker-compose -f "$DOCKER_COMPOSE_FILE" down 2>&1 | tee -a "$LOG_FILE"
        fi
        
        # Also stop production containers if they exist
        if [ -f "$DOCKER_COMPOSE_PROD_FILE" ]; then
            log_info "Stopping production containers"
            docker-compose -f "$DOCKER_COMPOSE_PROD_FILE" down 2>&1 | tee -a "$LOG_FILE"
        fi
    fi
    
    log_success "Project stopped successfully"
}

# Function to run tests
run_tests() {
    log_info "Running Django FBF tests..."
    
    cd "$PROJECT_DIR"
    
    # Set up Python virtual environment if it exists
    if [ -d "./venv" ]; then
        log_info "Activating virtual environment"
        source ./venv/bin/activate
    fi
    
    # Method 1: Try using our custom test runner
    if [ -f "$TEST_DIR/run_tests.py" ]; then
        log_info "Running tests using custom test runner"
        if python3 "$TEST_DIR/run_tests.py" 2>&1 | tee -a "$LOG_FILE"; then
            log_success "Custom test runner completed successfully"
            return 0
        else
            log_warning "Custom test runner failed, trying Django manage.py"
        fi
    fi
    
    # Method 2: Try using Django's manage.py test command
    if [ -f "$APP_DIR/manage.py" ]; then
        log_info "Running tests using Django manage.py"
        cd "$APP_DIR"
        
        # Set Django settings module for testing
        export DJANGO_SETTINGS_MODULE="core.settings"
        
        # Run Django tests
        if python3 manage.py test test --verbosity=2 --keepdb 2>&1 | tee -a "$LOG_FILE"; then
            log_success "Django tests completed successfully"
            return 0
        else
            log_error "Django tests failed"
            return 1
        fi
    fi
    
    # Method 3: Try using pytest if installed
    log_info "Trying pytest as fallback"
    if command -v pytest &> /dev/null; then
        cd "$TEST_DIR"
        if pytest -v 2>&1 | tee -a "$LOG_FILE"; then
            log_success "Pytest completed successfully"
            return 0
        else
            log_error "Pytest failed"
            return 1
        fi
    fi
    
    log_error "No suitable test runner found"
    return 1
}

# Function to check code quality (optional)
check_code_quality() {
    log_info "Checking code quality..."
    
    cd "$PROJECT_DIR"
    
    # Check if flake8 is available
    if command -v flake8 &> /dev/null; then
        log_info "Running flake8 linter"
        if flake8 app/ --max-line-length=88 --exclude=migrations 2>&1 | tee -a "$LOG_FILE"; then
            log_success "Code quality check passed"
        else
            log_warning "Code quality issues found (not blocking)"
        fi
    else
        log_info "flake8 not available, skipping code quality check"
    fi
}

# Function to start the project
start_project() {
    log_info "Starting Django FBF project..."
    
    cd "$PROJECT_DIR"
    
    # Start using existing start script if available
    if [ -f "./start_project.sh" ]; then
        log_info "Using existing start_project.sh script"
        if ./start_project.sh 2>&1 | tee -a "$LOG_FILE"; then
            log_success "Project started successfully using start script"
            return 0
        else
            log_error "Failed to start project using start script"
            return 1
        fi
    else
        # Start using docker-compose
        if [ -f "$DOCKER_COMPOSE_FILE" ]; then
            log_info "Starting containers using docker-compose"
            if docker-compose -f "$DOCKER_COMPOSE_FILE" up -d 2>&1 | tee -a "$LOG_FILE"; then
                log_success "Containers started successfully"
                
                # Wait a moment for containers to be ready
                log_info "Waiting for containers to be ready..."
                sleep 10
                
                # Check if containers are running
                if docker-compose -f "$DOCKER_COMPOSE_FILE" ps | grep -q "Up"; then
                    log_success "Containers are running"
                    return 0
                else
                    log_error "Containers failed to start properly"
                    return 1
                fi
            else
                log_error "Failed to start containers"
                return 1
            fi
        else
            log_error "No docker-compose.yaml file found"
            return 1
        fi
    fi
}

# Function to verify project is running
verify_project() {
    log_info "Verifying project is running..."
    
    # Check if containers are running
    cd "$PROJECT_DIR"
    if [ -f "$DOCKER_COMPOSE_FILE" ]; then
        if docker-compose -f "$DOCKER_COMPOSE_FILE" ps | grep -q "Up"; then
            log_success "Project containers are running"
            
            # Try to check if web service is responding
            log_info "Checking web service availability..."
            sleep 5
            
            # Try to curl the application (adjust port as needed)
            if curl -f -s http://localhost:8000 > /dev/null 2>&1; then
                log_success "Web service is responding"
            elif curl -f -s http://localhost:80 > /dev/null 2>&1; then
                log_success "Web service is responding on port 80"
            else
                log_warning "Web service may not be responding yet (this might be normal)"
            fi
            
            return 0
        else
            log_error "Project containers are not running"
            return 1
        fi
    fi
    
    log_warning "Could not verify project status"
    return 0
}

# Function to create backup before rebuild
create_backup() {
    log_info "Creating backup before rebuild..."
    
    cd "$PROJECT_DIR"
    
    # Create backup directory
    BACKUP_DIR="$PROJECT_DIR/backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Backup database if possible
    if [ -f "./bin/backupDB" ]; then
        log_info "Creating database backup"
        if ./bin/backupDB 2>&1 | tee -a "$LOG_FILE"; then
            log_success "Database backup created"
        else
            log_warning "Database backup failed"
        fi
    fi
    
    # Backup important files
    log_info "Backing up configuration files"
    cp -r app/ "$BACKUP_DIR/" 2>/dev/null || true
    cp docker-compose.yaml "$BACKUP_DIR/" 2>/dev/null || true
    cp docker-compose.prod.yml "$BACKUP_DIR/" 2>/dev/null || true
    
    log_success "Backup created in $BACKUP_DIR"
}

# Function to show project status
show_status() {
    log_info "Project Status:"
    echo "===========================================" | tee -a "$LOG_FILE"
    
    cd "$PROJECT_DIR"
    
    if [ -f "$DOCKER_COMPOSE_FILE" ]; then
        echo "Docker Containers:" | tee -a "$LOG_FILE"
        docker-compose -f "$DOCKER_COMPOSE_FILE" ps 2>&1 | tee -a "$LOG_FILE"
        echo "" | tee -a "$LOG_FILE"
    fi
    
    echo "Recent log entries:" | tee -a "$LOG_FILE"
    tail -10 "$LOG_FILE"
    echo "===========================================" | tee -a "$LOG_FILE"
}

# Main execution
main() {
    log_info "Starting Django FBF project rebuild process"
    log_info "Log file: $LOG_FILE"
    
    # Parse command line arguments
    SKIP_BACKUP=false
    SKIP_QUALITY_CHECK=false
    FORCE_RESTART=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-backup)
                SKIP_BACKUP=true
                shift
                ;;
            --skip-quality-check)
                SKIP_QUALITY_CHECK=true
                shift
                ;;
            --force-restart)
                FORCE_RESTART=true
                shift
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  --skip-backup           Skip backup creation"
                echo "  --skip-quality-check    Skip code quality check"
                echo "  --force-restart         Restart even if tests fail"
                echo "  --help                  Show this help message"
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Start rebuild process
    trap 'log_error "Rebuild process interrupted"; exit 1' INT TERM
    
    # Step 1: Check prerequisites
    check_docker
    
    # Step 2: Create backup (optional)
    if [ "$SKIP_BACKUP" = false ]; then
        create_backup
    else
        log_info "Skipping backup creation"
    fi
    
    # Step 3: Stop the project
    stop_project
    
    # Step 4: Run tests
    if run_tests; then
        log_success "All tests passed!"
        
        # Step 5: Check code quality (optional)
        if [ "$SKIP_QUALITY_CHECK" = false ]; then
            check_code_quality
        else
            log_info "Skipping code quality check"
        fi
        
        # Step 6: Start the project
        if start_project; then
            # Step 7: Verify project is running
            if verify_project; then
                log_success "Project rebuild completed successfully!"
                show_status
                exit 0
            else
                log_error "Project verification failed"
                exit 1
            fi
        else
            log_error "Failed to start project"
            exit 1
        fi
    else
        log_error "Tests failed!"
        
        if [ "$FORCE_RESTART" = true ]; then
            log_warning "Force restart enabled, starting project anyway"
            if start_project; then
                log_warning "Project started despite test failures"
                show_status
                exit 2  # Different exit code to indicate tests failed but project started
            else
                log_error "Failed to start project even with force restart"
                exit 1
            fi
        else
            log_error "Project not restarted due to test failures"
            log_info "Use --force-restart to start anyway"
            exit 1
        fi
    fi
}

# Handle help request
if [[ "${1:-}" == "--help" ]] || [[ "${1:-}" == "-h" ]]; then
    echo "Django FBF Project Rebuild Script"
    echo "=================================="
    echo ""
    echo "This script performs a complete rebuild of the Django FBF project:"
    echo "1. Creates a backup (optional)"
    echo "2. Stops the running project"
    echo "3. Runs all tests"
    echo "4. Checks code quality (optional)"
    echo "5. Restarts the project if tests pass"
    echo "6. Verifies the project is running"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --skip-backup           Skip backup creation before rebuild"
    echo "  --skip-quality-check    Skip code quality check with flake8"
    echo "  --force-restart         Restart project even if tests fail"
    echo "  --help, -h              Show this help message"
    echo ""
    echo "Exit codes:"
    echo "  0 - Success"
    echo "  1 - Error or tests failed"
    echo "  2 - Tests failed but project started (with --force-restart)"
    echo ""
    echo "Log files are created in the project directory with timestamp."
    exit 0
fi

# Run main function
main "$@"
