/**
 * Contact Page JavaScript
 * Handles contact form submission and FAQ interactions
 */

class ContactFormManager {
    constructor() {
        this.form = document.getElementById('contact-form');
        this.isSubmitting = false;
        this.init();
    }

    init() {
        if (this.form) {
            this.form.addEventListener('submit', (e) => this.handleSubmit(e));
            this.setupValidation();
        }
        
        this.setupFAQ();
        console.log('📧 Contact form initialized');
    }

    async handleSubmit(e) {
        e.preventDefault();
        
        if (this.isSubmitting) return;
        
        // Get form data
        const formData = {
            name: document.getElementById('name').value.trim(),
            email: document.getElementById('email').value.trim(),
            subject: document.getElementById('subject').value.trim(),
            message: document.getElementById('message').value.trim()
        };
        
        // Validate
        const errors = this.validateForm(formData);
        if (errors.length > 0) {
            errors.forEach(error => {
                window.AppUtils.showToast(error, 'error');
            });
            return;
        }
        
        // Set submitting state
        this.setSubmitting(true);
        
        try {
            // Simulate API call (replace with actual endpoint if needed)
            await this.submitForm(formData);
            
            // Show success message
            window.AppUtils.showToast('Message sent successfully! We\'ll get back to you soon.', 'success', 6000);
            
            // Reset form
            this.form.reset();
            
        } catch (error) {
            window.AppUtils.showToast(`Failed to send message: ${error.message}`, 'error');
        } finally {
            this.setSubmitting(false);
        }
    }

    validateForm(data) {
        const errors = [];
        
        // Name validation
        if (!data.name || data.name.length < 2) {
            errors.push('Please enter a valid name (at least 2 characters)');
        }
        
        // Email validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!data.email || !emailRegex.test(data.email)) {
            errors.push('Please enter a valid email address');
        }
        
        // Subject validation
        if (!data.subject || data.subject.length < 3) {
            errors.push('Please enter a subject (at least 3 characters)');
        }
        
        // Message validation
        if (!data.message || data.message.length < 10) {
            errors.push('Please enter a message (at least 10 characters)');
        }
        
        return errors;
    }

    setupValidation() {
        // Real-time validation feedback
        const fields = ['name', 'email', 'subject', 'message'];
        
        fields.forEach(fieldName => {
            const field = document.getElementById(fieldName);
            if (!field) return;
            
            field.addEventListener('blur', () => {
                this.validateField(fieldName, field.value.trim());
            });
            
            field.addEventListener('input', () => {
                // Clear error state on input
                this.clearFieldError(field);
            });
        });
    }

    validateField(fieldName, value) {
        const field = document.getElementById(fieldName);
        if (!field) return;
        
        let isValid = true;
        let errorMessage = '';
        
        switch (fieldName) {
            case 'name':
                isValid = value.length >= 2;
                errorMessage = 'Name must be at least 2 characters';
                break;
            case 'email':
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                isValid = emailRegex.test(value);
                errorMessage = 'Please enter a valid email address';
                break;
            case 'subject':
                isValid = value.length >= 3;
                errorMessage = 'Subject must be at least 3 characters';
                break;
            case 'message':
                isValid = value.length >= 10;
                errorMessage = 'Message must be at least 10 characters';
                break;
        }
        
        if (!isValid && value.length > 0) {
            this.showFieldError(field, errorMessage);
        } else {
            this.clearFieldError(field);
        }
        
        return isValid;
    }

    showFieldError(field, message) {
        field.classList.add('error');
        
        // Remove existing error message
        const existingError = field.parentElement.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
        
        // Add error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error';
        errorDiv.textContent = message;
        field.parentElement.appendChild(errorDiv);
    }

    clearFieldError(field) {
        field.classList.remove('error');
        const errorDiv = field.parentElement.querySelector('.field-error');
        if (errorDiv) {
            errorDiv.remove();
        }
    }

    async submitForm(formData) {
        // Simulate API call with delay
        // In production, replace this with actual API endpoint
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                console.log('Form submitted:', formData);
                
                // Simulate 95% success rate
                if (Math.random() < 0.95) {
                    resolve({ success: true });
                } else {
                    reject(new Error('Network error. Please try again.'));
                }
            }, 1500);
        });
        
        // Example of actual API call:
        /*
        const response = await fetch('/api/contact', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            throw new Error('Failed to submit form');
        }
        
        return await response.json();
        */
    }

    setSubmitting(submitting) {
        this.isSubmitting = submitting;
        
        const submitButton = this.form.querySelector('button[type="submit"]');
        const buttonText = submitButton.querySelector('.button-text');
        const buttonIcon = submitButton.querySelector('i');
        
        if (submitting) {
            submitButton.disabled = true;
            buttonText.textContent = 'Sending...';
            buttonIcon.className = 'fas fa-spinner fa-spin';
        } else {
            submitButton.disabled = false;
            buttonText.textContent = 'Send Message';
            buttonIcon.className = 'fas fa-paper-plane';
        }
        
        // Disable all form fields
        const formFields = this.form.querySelectorAll('input, textarea');
        formFields.forEach(field => {
            field.disabled = submitting;
        });
    }

    setupFAQ() {
        const faqItems = document.querySelectorAll('.faq-item');
        
        faqItems.forEach(item => {
            const question = item.querySelector('.faq-question');
            
            question.addEventListener('click', () => {
                // Toggle current item
                const isActive = item.classList.contains('active');
                
                // Close all items
                faqItems.forEach(i => i.classList.remove('active'));
                
                // Open clicked item if it wasn't active
                if (!isActive) {
                    item.classList.add('active');
                }
            });
        });
    }
}

// Character counter for textarea
class CharacterCounter {
    constructor(textareaId, maxLength = 1000) {
        this.textarea = document.getElementById(textareaId);
        this.maxLength = maxLength;
        this.init();
    }

    init() {
        if (!this.textarea) return;
        
        // Create counter element
        const counter = document.createElement('div');
        counter.className = 'character-counter';
        counter.textContent = `0 / ${this.maxLength}`;
        this.textarea.parentElement.appendChild(counter);
        
        // Update counter on input
        this.textarea.addEventListener('input', () => {
            const length = this.textarea.value.length;
            counter.textContent = `${length} / ${this.maxLength}`;
            
            if (length > this.maxLength * 0.9) {
                counter.classList.add('warning');
            } else {
                counter.classList.remove('warning');
            }
            
            if (length >= this.maxLength) {
                counter.classList.add('error');
            } else {
                counter.classList.remove('error');
            }
        });
        
        // Enforce max length
        this.textarea.setAttribute('maxlength', this.maxLength);
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize if we're on the contact page
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        const contactFormManager = new ContactFormManager();
        const messageCounter = new CharacterCounter('message', 1000);
    }
});
