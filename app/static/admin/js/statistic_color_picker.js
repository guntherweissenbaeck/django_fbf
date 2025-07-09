// Erweiterte Farbauswahl-Funktionalität für Statistik-Admin

document.addEventListener('DOMContentLoaded', function() {
    // Warte kurz, damit alle Django-Admin-Skripte geladen sind
    setTimeout(function() {
        const colorField = document.querySelector('input[name="color"]');
        
        if (colorField && !colorField.dataset.enhanced) {
            // Markiere als bereits erweitert
            colorField.dataset.enhanced = 'true';
            
            // Erstelle Container für erweiterte Farbauswahl
            const container = document.createElement('div');
            container.className = 'color-picker-container';
            
            // Erstelle Color Picker
            const colorPicker = document.createElement('input');
            colorPicker.type = 'color';
            colorPicker.className = 'color-picker-input';
            colorPicker.value = colorField.value || '#28a745';
            
            // Erstelle Farb-Vorschau
            const colorPreview = document.createElement('div');
            colorPreview.className = 'color-preview';
            colorPreview.style.backgroundColor = colorField.value || '#28a745';
            
            // Erstelle vordefinierte Farbpalette
            const colorPalette = document.createElement('div');
            colorPalette.className = 'color-palette';
            colorPalette.innerHTML = `
                <div style="margin-top: 15px; padding: 10px; background-color: #f8f9fa; border-radius: 6px;">
                    <strong style="color: #333; margin-bottom: 8px; display: block;">Vordefinierte Farben:</strong>
                    <div style="display: flex; gap: 8px; margin-top: 8px; flex-wrap: wrap;">
                        <button type="button" class="quick-color" data-color="#28a745" style="background: #28a745;" title="Grün (Gerettet)">✓</button>
                        <button type="button" class="quick-color" data-color="#dc3545" style="background: #dc3545;" title="Rot (Verstorben)">×</button>
                        <button type="button" class="quick-color" data-color="#ffc107" style="background: #ffc107;" title="Gelb (In Behandlung)">⚕</button>
                        <button type="button" class="quick-color" data-color="#007bff" style="background: #007bff;" title="Blau">💙</button>
                        <button type="button" class="quick-color" data-color="#6f42c1" style="background: #6f42c1;" title="Lila">💜</button>
                        <button type="button" class="quick-color" data-color="#fd7e14" style="background: #fd7e14;" title="Orange">🧡</button>
                        <button type="button" class="quick-color" data-color="#20c997" style="background: #20c997;" title="Türkis">💚</button>
                        <button type="button" class="quick-color" data-color="#6c757d" style="background: #6c757d;" title="Grau">⚫</button>
                    </div>
                </div>
            `;
            
            // Styling für Schnellauswahl-Buttons
            if (!document.getElementById('color-picker-styles')) {
                const style = document.createElement('style');
                style.id = 'color-picker-styles';
                style.textContent = `
                    .color-picker-container {
                        display: flex;
                        align-items: center;
                        gap: 15px;
                        margin: 10px 0;
                        padding: 10px;
                        background-color: #f0f0f0;
                        border-radius: 8px;
                        border: 1px solid #ddd;
                    }
                    
                    .color-picker-input {
                        width: 60px !important;
                        height: 40px !important;
                        border: 2px solid #ddd !important;
                        border-radius: 8px !important;
                        cursor: pointer !important;
                        padding: 0 !important;
                    }
                    
                    .color-preview {
                        width: 40px;
                        height: 40px;
                        border-radius: 50%;
                        border: 3px solid #fff;
                        box-shadow: 0 2px 6px rgba(0,0,0,0.15);
                        display: inline-block;
                    }
                    
                    .quick-color {
                        width: 40px !important;
                        height: 40px !important;
                        border: 3px solid #fff !important;
                        border-radius: 50% !important;
                        cursor: pointer !important;
                        color: white !important;
                        font-weight: bold !important;
                        font-size: 14px !important;
                        box-shadow: 0 3px 6px rgba(0,0,0,0.2) !important;
                        transition: all 0.2s ease !important;
                        margin: 3px !important;
                        outline: none !important;
                    }
                    
                    .quick-color:hover {
                        transform: scale(1.15) !important;
                        border-color: #333 !important;
                        box-shadow: 0 4px 8px rgba(0,0,0,0.3) !important;
                    }
                    
                    .quick-color:active {
                        transform: scale(0.95) !important;
                    }
                `;
                document.head.appendChild(style);
            }
            
            // Organisiere das Layout
            const fieldContainer = colorField.closest('.field-color') || colorField.parentNode;
            
            // Füge Label hinzu
            const label = document.createElement('div');
            label.innerHTML = '<strong style="color: #333; margin-bottom: 5px; display: block;">🎨 Farbauswahl:</strong>';
            
            container.appendChild(colorPicker);
            container.appendChild(colorPreview);
            
            // Füge Container vor dem ursprünglichen Feld ein
            fieldContainer.insertBefore(label, colorField);
            fieldContainer.insertBefore(container, colorField);
            fieldContainer.appendChild(colorPalette);
            
            // Aktualisiere das ursprüngliche Textfeld für bessere Sichtbarkeit
            colorField.style.cssText = `
                width: 140px !important;
                font-family: 'Monaco', 'Menlo', 'Consolas', 'Courier New', monospace !important;
                font-size: 16px !important;
                font-weight: bold !important;
                text-transform: uppercase !important;
                letter-spacing: 2px !important;
                padding: 12px 15px !important;
                border: 2px solid #007cba !important;
                border-radius: 8px !important;
                background-color: #fff !important;
                margin-top: 10px !important;
                text-align: center !important;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
            `;
            
            // Event Listeners
            
            // Color Picker ändert Textfeld und Vorschau
            colorPicker.addEventListener('input', function() {
                const color = this.value.toUpperCase();
                colorField.value = color;
                colorPreview.style.backgroundColor = color;
            });
            
            // Textfeld ändert Color Picker und Vorschau
            colorField.addEventListener('input', function() {
                let color = this.value.trim().toUpperCase();
                if (!color.startsWith('#') && color.length > 0) {
                    color = '#' + color;
                    this.value = color;
                }
                
                if (/^#[0-9A-Fa-f]{6}$/.test(color)) {
                    colorPicker.value = color;
                    colorPreview.style.backgroundColor = color;
                }
            });
            
            // Schnellauswahl-Buttons
            document.querySelectorAll('.quick-color').forEach(button => {
                button.addEventListener('click', function(e) {
                    e.preventDefault();
                    const color = this.dataset.color.toUpperCase();
                    colorField.value = color;
                    colorPicker.value = color;
                    colorPreview.style.backgroundColor = color;
                    
                    // Visuelles Feedback
                    this.style.transform = 'scale(0.9)';
                    setTimeout(() => {
                        this.style.transform = 'scale(1)';
                    }, 150);
                });
            });
            
            // Validierung des Hex-Werts
            colorField.addEventListener('blur', function() {
                let color = this.value.trim().toUpperCase();
                
                // Füge # hinzu falls vergessen
                if (color && !color.startsWith('#')) {
                    color = '#' + color;
                }
                
                // Validiere Hex-Format
                if (color && !/^#[0-9A-Fa-f]{6}$/.test(color)) {
                    alert('Bitte geben Sie einen gültigen Hex-Farbcode ein (z.B. #28A745)');
                    this.focus();
                    return;
                }
                
                if (color) {
                    this.value = color;
                    colorPicker.value = color;
                    colorPreview.style.backgroundColor = color;
                }
            });
            
            // Initialisiere mit aktuellem Wert
            const currentColor = (colorField.value || '#28A745').toUpperCase();
            colorField.value = currentColor;
            colorPicker.value = currentColor;
            colorPreview.style.backgroundColor = currentColor;
        }
    }, 100);
});
