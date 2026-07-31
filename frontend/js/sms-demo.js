const SMS_TEMPLATES = {
  flood: {
    phone: '+254712345678',
    message: 'Maji yamefurika katika kijiji chetu. Maji yameingia nyumbani karibu na mto. Tunahitaji msaada.',
  },
  drought: {
    phone: '+254723456789',
    message: 'Hakuna mvua kwa miezi mitatu. Mazao yanakauka na mifugo haina maji. Jumuiya yetu inakabiliwa na ukame mkali.',
  },
  pest: {
    phone: '+254734567890',
    message: 'Nzige wamevamia mashamba yetu. Wanakula mazao yote. Tunahitaji msaada wa kudhibiti wadudu hawa.',
  },
  disease: {
    phone: '+254745678901',
    message: 'Watu wengi katika kijiji chetu ni wagonjwa wa homa na kuhara. Tunafikiri ni kipindupindu. Tunahitaji msaada wa matibabu.',
  },
  fire: {
    phone: '+254756789012',
    message: 'Moto unaenea karibu na kijiji chetu. Upepo ni mkali na moto unaelekea kwenye nyumba. Tunahitaji msaada wa haraka.',
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
