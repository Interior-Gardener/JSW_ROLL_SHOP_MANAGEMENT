// document.getElementById("loginForm").addEventListener("submit", async function (e) {
//     e.preventDefault();

//     const employeeid = document.getElementById("id").value;  // matches your input id="id"
//     const password = document.getElementById("password").value;

//     const response = await fetch("/login", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ employeeid, password })  // key should be employeeid to match backend
//     });

//     const result = await response.json();

//     if (result.success) {
//         window.location.href = "/homepage";
//     } else {
//         alert("Invalid ID or password");
//         animateShake(document.getElementById("id"));
//         animateShake(document.getElementById("password"));
//     }
// });

function animateShake(element) {
    element.style.borderColor = 'var(--danger-color)';
    element.style.animation = 'shake 0.5s';

    setTimeout(() => {
        element.style.animation = '';
        element.style.borderColor = '';
    }, 500);
}

document.head.insertAdjacentHTML('beforeend', `
    <style>
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
            20%, 40%, 60%, 80% { transform: translateX(5px); }
        }
    </style>
`);
