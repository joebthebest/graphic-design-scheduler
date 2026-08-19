/**
 * Graphic Design Booking Wizard - Interactive Stepper & Slot Engine
 */

document.addEventListener('DOMContentLoaded', () => {
  let currentStep = 1;
  const totalSteps = 3;

  // DOM Elements
  const wizardForm = document.getElementById('booking-wizard-form');
  const stepItems = document.querySelectorAll('.step-item');
  const wizardSteps = document.querySelectorAll('.wizard-step');
  const progressFill = document.getElementById('stepper-progress-fill');
  
  const btnPrev = document.getElementById('btn-prev');
  const btnNext = document.getElementById('btn-next');
  const btnSubmit = document.getElementById('btn-submit');

  // Hidden / Form Inputs
  const serviceInput = document.getElementById('id_service');
  const dateInput = document.getElementById('id_appointment_date');
  const timeInput = document.getElementById('id_start_time');

  // Service Selection Cards
  const serviceCards = document.querySelectorAll('.service-select-card');
  const slotsContainer = document.getElementById('slots-container');
  const slotsLoading = document.getElementById('slots-loading');
  const slotsEmpty = document.getElementById('slots-empty');
  
  // Morning / Afternoon / Evening buckets
  const morningSlotsEl = document.getElementById('morning-slots');
  const afternoonSlotsEl = document.getElementById('afternoon-slots');
  const eveningSlotsEl = document.getElementById('evening-slots');
  const morningSection = document.getElementById('morning-section');
  const afternoonSection = document.getElementById('afternoon-section');
  const eveningSection = document.getElementById('evening-section');

  // Step 3 Summary Elements
  const summaryService = document.getElementById('summary-service-name');
  const summaryPrice = document.getElementById('summary-service-price');
  const summaryDuration = document.getElementById('summary-service-duration');
  const summaryDate = document.getElementById('summary-date');
  const summaryTime = document.getElementById('summary-time');

  // 1. Service Card Selection
  serviceCards.forEach(card => {
    card.addEventListener('click', () => {
      serviceCards.forEach(c => c.classList.remove('selected'));
      card.classList.add('selected');

      const serviceId = card.getAttribute('data-service-id');
      const serviceName = card.getAttribute('data-service-name');
      const servicePrice = card.getAttribute('data-service-price');
      const serviceDuration = card.getAttribute('data-service-duration');

      if (serviceInput) serviceInput.value = serviceId;

      if (summaryService) summaryService.textContent = serviceName;
      if (summaryPrice) summaryPrice.textContent = servicePrice;
      if (summaryDuration) summaryDuration.textContent = `${serviceDuration} Min Consultation`;

      // Refresh slots if date is selected
      if (dateInput && dateInput.value) {
        fetchAvailableSlots();
      }
    });
  });

  // 2. Date Input Change Handler
  if (dateInput) {
    // Set min date to today
    const todayStr = new Date().toISOString().split('T')[0];
    dateInput.min = todayStr;
    if (!dateInput.value) {
      dateInput.value = todayStr;
    }

    dateInput.addEventListener('change', () => {
      fetchAvailableSlots();
      if (summaryDate) summaryDate.textContent = formatDate(dateInput.value);
    });
  }

  // 3. Dynamic Slot Fetch via API
  function fetchAvailableSlots() {
    const selectedServiceCard = document.querySelector('.service-select-card.selected');
    const serviceId = selectedServiceCard ? selectedServiceCard.getAttribute('data-service-id') : (serviceInput ? serviceInput.value : null);
    const dateVal = dateInput ? dateInput.value : null;

    if (!serviceId || !dateVal) return;

    if (slotsLoading) slotsLoading.style.display = 'block';
    if (slotsContainer) slotsContainer.style.display = 'none';
    if (slotsEmpty) slotsEmpty.style.display = 'none';

    fetch(`/schedule/api/available-slots/?service_id=${serviceId}&date=${dateVal}`)
      .then(res => res.json())
      .then(data => {
        if (slotsLoading) slotsLoading.style.display = 'none';

        if (data.status === 'success' && data.slots && data.slots.length > 0) {
          renderSlots(data.slots);
          if (slotsContainer) slotsContainer.style.display = 'block';
        } else {
          if (slotsEmpty) slotsEmpty.style.display = 'block';
        }
      })
      .catch(err => {
        console.error('Error fetching available slots:', err);
        if (slotsLoading) slotsLoading.style.display = 'none';
        if (slotsEmpty) slotsEmpty.style.display = 'block';
      });
  }

  function renderSlots(slots) {
    if (morningSlotsEl) morningSlotsEl.innerHTML = '';
    if (afternoonSlotsEl) afternoonSlotsEl.innerHTML = '';
    if (eveningSlotsEl) eveningSlotsEl.innerHTML = '';

    let mCount = 0, aCount = 0, eCount = 0;

    slots.forEach(slot => {
      const chip = document.createElement('button');
      chip.type = 'button';
      chip.className = 'slot-chip';
      chip.textContent = slot.start_formatted;
      chip.setAttribute('data-time', slot.start_time);
      chip.setAttribute('data-formatted', slot.start_formatted);

      if (timeInput && timeInput.value === slot.start_time) {
        chip.classList.add('selected');
      }

      chip.addEventListener('click', () => {
        document.querySelectorAll('.slot-chip').forEach(c => c.classList.remove('selected'));
        chip.classList.add('selected');
        if (timeInput) timeInput.value = slot.start_time;
        if (summaryTime) summaryTime.textContent = slot.start_formatted;
      });

      const hour = parseInt(slot.start_time.split(':')[0], 10);
      if (hour < 12) {
        if (morningSlotsEl) morningSlotsEl.appendChild(chip);
        mCount++;
      } else if (hour < 17) {
        if (afternoonSlotsEl) afternoonSlotsEl.appendChild(chip);
        aCount++;
      } else {
        if (eveningSlotsEl) eveningSlotsEl.appendChild(chip);
        eCount++;
      }
    });

    if (morningSection) morningSection.style.display = mCount > 0 ? 'block' : 'none';
    if (afternoonSection) afternoonSection.style.display = aCount > 0 ? 'block' : 'none';
    if (eveningSection) eveningSection.style.display = eCount > 0 ? 'block' : 'none';
  }

  function formatDate(dStr) {
    if (!dStr) return '-';
    const dateObj = new Date(dStr + 'T00:00:00');
    return dateObj.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' });
  }

  // 4. Stepper Navigation Logic
  function updateStepUI() {
    wizardSteps.forEach((step, idx) => {
      step.classList.toggle('active', idx + 1 === currentStep);
    });

    stepItems.forEach((item, idx) => {
      item.classList.toggle('active', idx + 1 === currentStep);
      item.classList.toggle('completed', idx + 1 < currentStep);
    });

    if (progressFill) {
      const percentage = ((currentStep - 1) / (totalSteps - 1)) * 100;
      progressFill.style.width = `${percentage}%`;
    }

    if (btnPrev) btnPrev.style.display = currentStep > 1 ? 'inline-flex' : 'none';
    if (btnNext) btnNext.style.display = currentStep < totalSteps ? 'inline-flex' : 'none';
    if (btnSubmit) btnSubmit.style.display = currentStep === totalSteps ? 'inline-flex' : 'none';

    // Update summary preview
    if (summaryDate && dateInput) summaryDate.textContent = formatDate(dateInput.value);
    if (summaryTime && timeInput && timeInput.value) {
      const selectedChip = document.querySelector('.slot-chip.selected');
      summaryTime.textContent = selectedChip ? selectedChip.textContent : timeInput.value;
    }
  }

  function validateStep(step) {
    if (step === 1) {
      const selectedService = document.querySelector('.service-select-card.selected');
      if (!selectedService && (!serviceInput || !serviceInput.value)) {
        alert('Please select a Graphic Design service package to proceed.');
        return false;
      }
      return true;
    }
    if (step === 2) {
      if (!dateInput || !dateInput.value) {
        alert('Please pick a consultation date.');
        return false;
      }
      if (!timeInput || !timeInput.value) {
        alert('Please select an available time slot.');
        return false;
      }
      return true;
    }
    return true;
  }

  if (btnNext) {
    btnNext.addEventListener('click', () => {
      if (validateStep(currentStep)) {
        if (currentStep < totalSteps) {
          currentStep++;
          updateStepUI();
          window.scrollTo({ top: 150, behavior: 'smooth' });
        }
      }
    });
  }

  if (btnPrev) {
    btnPrev.addEventListener('click', () => {
      if (currentStep > 1) {
        currentStep--;
        updateStepUI();
        window.scrollTo({ top: 150, behavior: 'smooth' });
      }
    });
  }

  // Initialize Slots on First Load
  fetchAvailableSlots();
  updateStepUI();
});
