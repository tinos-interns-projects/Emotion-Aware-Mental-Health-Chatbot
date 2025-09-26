function scrollToBottom() {
    $("#chat-box").scrollTop($("#chat-box")[0].scrollHeight);
}

$(document).ready(function() {
    scrollToBottom();

    // ---------------- Send Message ----------------
    $("#chat-form").submit(function(e) {
        e.preventDefault();
        const message = $("#user-input").val().trim();
        if (!message) return;

        // Show user message
        $("#chat-box").append('<div class="message user-msg">' + message + '</div>');
        scrollToBottom();
        $("#user-input").val("");

        // Send message to server
        $.post($(this).attr("action"), {
            message: message,
            csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
        }).done(function(data) {
            if (data.reply) {
                const botDiv = $('<div class="message bot-msg"></div>').appendTo("#chat-box");
                scrollToBottom();
                const words = data.reply.split(" ");
                let i = 0;

                function typeWord() {
                    if (i < words.length) {
                        botDiv.append(words[i] + " ");
                        i++;
                        scrollToBottom();
                        setTimeout(typeWord, 150);
                    }
                }
                typeWord();
            }
        });
    });

    // ---------------- Clear History ----------------
    $("#clear-btn").click(function() {
        if (confirm("Are you sure you want to clear chat history?")) {
            $.post($(this).data("url"), {
                csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
            }).done(function() {
                $("#chat-box").html("<p id='clear-msg'>No messages yet. Start the conversation!</p>");

                // Remove the message after 2 seconds
                setTimeout(function() {
                    $("#clear-msg").fadeOut("slow", function() {
                        $(this).remove();
                    });
                }, 2000);
            });
        }
    });


    // ---------------- Profile Dropdown ----------------
    $("#profile-link").click(function(e) {
        e.stopPropagation();
        $("#profile-dropdown").toggle();
    });

    $(document).click(function() {
        $("#profile-dropdown").hide();
    });

    // ---------------- Flash Messages ----------------
    setTimeout(function() {
        const flash = document.getElementById("flash-messages");
        if (flash) {
            flash.style.transition = "opacity 0.5s ease";
            flash.style.opacity = "0";
            setTimeout(() => flash.remove(), 500);
        }
    }, 3000);

    // ---------------- Voice Recording ----------------
    let mediaRecorder;
    let audioChunks = [];
    let startTime, timerInterval;

    $("#record-btn").click(function() {
        if (!mediaRecorder || mediaRecorder.state === "inactive") {
            navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];

                mediaRecorder.ondataavailable = e => {
                    if (e.data.size > 0) {
                        audioChunks.push(e.data);
                    }
                };

                mediaRecorder.onstop = () => {
                    const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
                    const formData = new FormData();
                    formData.append("voice", audioBlob, "recording.webm");
                    formData.append("csrfmiddlewaretoken", $('input[name="csrfmiddlewaretoken"]').val());

                    $.ajax({
                        url: "/save-voice/",
                        type: "POST",
                        data: formData,
                        processData: false,
                        contentType: false,
                        success: function(res) {
                            if (res.status === "success") {
                                // ✅ Put transcribed text into the input box
                                $("#user-input").val(res.text);

                                // (optional) also log the file path
                                console.log("Recording saved at:", res.filepath);
                            } else {
                                alert("Error: " + res.message);
                            }
                        },
                        error: function() {
                            alert("Failed to save recording.");
                        }
                    });
                };

                mediaRecorder.start();

                // Start Timer
                startTime = Date.now();
                timerInterval = setInterval(() => {
                    const elapsed = Math.floor((Date.now() - startTime) / 1000);
                    $("#record-timer").text(elapsed + "s");
                }, 1000);

                $("#record-btn").html(`
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" 
         stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <rect x="6" y="6" width="12" height="12" rx="2"></rect>
    </svg> Stop
`);
            }).catch(err => {
                alert("Microphone access denied: " + err.message);
            });
        } else if (mediaRecorder.state === "recording") {
            mediaRecorder.stop();
            clearInterval(timerInterval);
            $("#record-timer").text("");
            $("#record-btn").html(`
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" 
             stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
          <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
          <line x1="12" y1="19" x2="12" y2="23"></line>
          <line x1="8" y1="23" x2="16" y2="23"></line>
        </svg> 
    `);
        }
    });
});

// ---------------- Text-to-Speech for "Read" button ----------------
$(document).on("click", ".read-btn", function() {
    const text = $(this).data("message");

    if (speechSynthesis.speaking) {
        speechSynthesis.cancel();
        return;
    }

    if ("speechSynthesis" in window) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.pitch = 1.2;
        utterance.rate = 0.9;
        utterance.volume = 1;
        utterance.lang = "hi-IN"; // Hindi (India)

        const voices = speechSynthesis.getVoices();
        const selectedVoice = voices.find(v => v.lang === "hi-IN" || v.name.toLowerCase().includes("hindi"));
        if (selectedVoice) utterance.voice = selectedVoice;

        speechSynthesis.speak(utterance);
    } else {
        alert("Sorry, your browser does not support text-to-speech.");
    }
});



setTimeout(function() {
    document.querySelectorAll('.flash-message').forEach(function(el) {
        el.style.display = 'none';
    });
}, 3000);

// Global Translate Chat Function
$(document).ready(function() {
    // Toggle language selector
    $('#translate-chat-btn').click(function() {
        $('.lang-select-global').toggle();
    });

    // Translate all chat messages
    $('#translate-chat-submit').click(function() {
        const lang = $('#chat-language').val();

        $('#chat-box .message').each(function() {
            const msgDiv = $(this);
            const span = msgDiv.find('.msg-text');
            const original = span.data('original') || span.text();
            span.attr('data-original', original); // store original

            $.ajax({
                url: "{% url 'translate_text' %}",
                type: "POST",
                data: {
                    'text': original,
                    'lang': lang,
                    'csrfmiddlewaretoken': '{{ csrf_token }}'
                },
                success: function(response) {
                    span.text(response.translated_text);
                },

            });
        });

        // Hide language selector after submit
        $('.lang-select-global').hide();
    });
});


function toggleSidebar() {
    let sidebar = document.getElementById("sidebar");
    let menuIcon = document.getElementById("menuIcon");

    if (sidebar.style.width === "250px") {
        sidebar.style.width = "0";
        menuIcon.style.display = "block";
    } else {
        sidebar.style.width = "250px";
        menuIcon.style.display = "none";
    }
}

// Close sidebar when clicking outside
document.addEventListener("click", function(event) {
    let sidebar = document.getElementById("sidebar");
    let menuIcon = document.getElementById("menuIcon");

    if (sidebar.style.width === "250px" &&
        !sidebar.contains(event.target) &&
        !menuIcon.contains(event.target)) {
        sidebar.style.width = "0";
        menuIcon.style.display = "block";
    }
});


document.addEventListener('DOMContentLoaded', function() {
    // Show dropdown on dots button click
    document.querySelectorAll('.dots-btn').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            // Close other dropdowns
            document.querySelectorAll('.dropdown-menu').forEach(function(menu) {
                menu.style.display = 'none';
            });
            // Show this dropdown
            btn.nextElementSibling.style.display = 'block';
        });
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', function() {
        document.querySelectorAll('.dropdown-menu').forEach(function(menu) {
            menu.style.display = 'none';
        });
    });

    // Prevent closing when clicking inside dropdown
    document.querySelectorAll('.dropdown-menu').forEach(function(menu) {
        menu.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    });
});