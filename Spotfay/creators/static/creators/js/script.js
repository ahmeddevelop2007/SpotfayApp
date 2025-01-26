document.getElementById('fileUpload').addEventListener('change', function (e) {
    const files = e.target.files;
    if (files.length > 0) {
      alert(`${files.length} file(s) selected`);
    }
  });

// Personal info modal script
let input = document.getElementById("custom-input")
let profile_modal = '{{user.user_profile.url}}'
let profile_modal_empty = '/default_photos/spotfay_pro_com.png'
let profile_holder_modal = document.getElementById("profile-holder-modal")
profile_holder_modal.addEventListener("click", function() {
    input.addEventListener("change", function() {
    const file = input.files[0];
    const reader = new FileReader();
    reader.onload = function() {
        const fileContent = reader.result;
        profile_holder_modal.innerHTML = `<img src="${fileContent}" class="rounded" alt="" style="height: auto;width: 100%">`;
    };
    reader.readAsDataURL(file);
    });
});