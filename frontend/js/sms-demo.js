const SMS_TEMPLATES = {
  flood: {
    phone: '+254712345678',
    message: 'Heavy rains have caused flooding in our village. Water is entering homes near the river. We need assistance.',
  },
  drought: {
    phone: '+254723456789',
    message: 'No rain for 3 months. Crops are dying and livestock have no water. Our community is facing severe drought.',
  },
  pest: {
    phone: '+254734567890',
    message: 'Locusts have invaded our farms. They are eating all the crops. We need help to control the infestation.',
  },
  disease: {
    phone: '+254745678901',
    message: 'Many people in our village are sick with fever and diarrhea. We think it might be cholera. Need medical help.',
  },
  fire: {
    phone: '+254756789012',
    message: 'A fire is spreading through the bush near our village. The wind is strong and it is moving towards homes.',
  },
};

function openSMSDemo() {
  document.getElementById('smsDemoModal').classList.add('open');
  document.body.style.overflow = 'hidden';
  fillSMSTemplate('flood');
}

function fillSMSTemplate(type) {
  const template = SMS_TEMPLATES[type];
  if (!template) return;

  document.getElementById('smsNumber').value = template.phone;
  document.getElementById('smsMessage').value = template.message;
}

async function sendSMSDemo() {
  const phone = document.getElementById('smsNumber').value.trim();
  const message = document.getElementById('smsMessage').value.trim();

  if (!phone || !message) {
    showNotification('Error', 'Please enter both phone number and message', 'error');
    return;
  }

  const btn = document.getElementById('smsSendBtn');
  btn.disabled = true;
  btn.textContent = 'Sending...';

  try {
    const result = await API.sendSMSWebhook(phone, message);

    const classificationEmoji = {
      flood: '🌊', drought: '☀️', pest: '🐛', disease: '🤒',
      fire: '🔥', conflict: '⚔️', health: '🏥', other: '📌',
    };

    const emoji = classificationEmoji[result.classification?.report_type] || '✅';
    showNotification(
      `${emoji} SMS Received by System!`,
      `Report ID: ${result.report_id?.substring(0, 8) || 'simulated'}... | Classified and added to map`,
      'success'
    );

    closeModal('smsDemoModal');

    await loadData();
  } catch (err) {
    if (API.getBaseUrl().includes('localhost')) {
      showNotification(
        'SMS Simulated (Offline)',
        'Backend not running - report added to demo mode',
        'info'
      );
      closeModal('smsDemoModal');

      const demoReport = {
        id: 'demo-' + Date.now(),
        message: message,
        source: 'sms',
        report_type: 'flood',
        severity: 'high',
        confidence: 0.85,
        latitude: -1.28 + (Math.random() - 0.5) * 2,
        longitude: 36.8 + (Math.random() - 0.5) * 2,
        location_name: 'Demo Location, Kenya',
        phone_number: phone,
        submitted_at: new Date().toISOString(),
      };

      appState.reports.unshift(demoReport);
      MapManager.addReportMarker(demoReport);
      updateStats();
      renderTabContent();
    } else {
      showNotification('Error', err.message || 'Failed to send SMS', 'error');
    }
  } finally {
    btn.disabled = false;
    btn.textContent = 'Send SMS';
  }
}
