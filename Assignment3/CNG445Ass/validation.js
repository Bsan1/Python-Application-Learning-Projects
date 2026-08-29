function toggleFee() {
  const paid = document.querySelector('input[name="fee_type"][value="paid"]');
  const feeBox = document.getElementById("feeInput");
  if (!paid || !feeBox) return;
  feeBox.style.display = paid.checked ? "block" : "none";
}

function validateEventForm() {
  const checked = document.querySelectorAll('input[name="societies"]:checked').length;
  if (checked === 0) {
    alert("Please select at least one society.");
    return false;
  }
  const paid = document.querySelector('input[name="fee_type"][value="paid"]');
  if (paid && paid.checked) {
    const fee = document.getElementById("entryPrice").value.trim();
    if (!/^\d+(\.\d+)?$/.test(fee)) {
      alert("Fee must be a number (e.g., 50 or 50.5).");
      return false;
    }
  }
  return true;
}

document.addEventListener("DOMContentLoaded", toggleFee);
