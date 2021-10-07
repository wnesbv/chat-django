let notify_badge_class;
let notify_menu_class;
let notify_api_url;
let notify_fetch_count;
let notify_unread_url;
let notify_mark_all_unread_url;
let notify_refresh_period = 15000;
let consecutive_misfires = 0;
const registered_functions = [];

function fill_notification_badge(data) {
    const badges = document.getElementsByClassName(notify_badge_class);
    if (badges) {
        for (let i = 0; i < badges.length; i++) {
            badges[i].innerHTML = data.unread_count;
        }
    }
}

function fill_notification_list(data) {
    const menus = document.getElementsByClassName(notify_menu_class);
    if (menus) {
        const messages = data.unread_list.map((item) => {
            let actor = '';
            let verb = '';
            let target = '';
            let timestamp = '';
            let action_object = '';
            if (typeof item.actor !== 'undefined') {
                actor = item.actor;
            }
            if (typeof item.verb !== 'undefined') {
                verb = `${verb} ${item.verb}`;
            }
            if (typeof item.target !== 'undefined') {
                target = `${target} ${item.target}`;
            }
            if (typeof item.timestamp !== 'undefined') {
                timestamp = `${timestamp} ${item.timestamp}`;
            }
            return `<li class="list-group-item"><span class="me-1"><i class="bi bi-person-fill me-1"></i>${actor}</span><span><i class="bi bi-check2-circle"></i>${verb}</span><a class="btn btn-sm btn-outline-primary mx-2" href="${target}"><i class="bi bi-arrow-up-right mx-1"></i></a><time><sup>${timestamp}</sup></time></li>`;
        }).join('')

        for (let i = 0; i < menus.length; i++) {
            menus[i].innerHTML = messages;
        }
    }
}

function register_notifier(func) {
    registered_functions.push(func);
}

function fetch_api_data() {
    if (registered_functions.length > 0) {
        // only fetch data if a function is setup
        const r = new XMLHttpRequest();
        r.addEventListener('readystatechange', function (event) {
            if (this.readyState === 4) {
                if (this.status === 200) {
                    consecutive_misfires = 0;
                    const data = JSON.parse(r.responseText);
                    for (let i = 0; i < registered_functions.length; i++) {
                       registered_functions[i](data);
                    }
                } else {
                    consecutive_misfires++;
                }
            }
        })
        r.open('GET', `${notify_api_url}?max=${notify_fetch_count}`, true);
        r.send();
    }
    if (consecutive_misfires < 10) {
        setTimeout(fetch_api_data, notify_refresh_period);
    } else {
        const badges = document.getElementsByClassName(notify_badge_class);
        if (badges) {
            for (let i = 0; i < badges.length; i++) {
                badges[i].innerHTML = '!';
                badges[i].title = 'Connection lost!'
            }
        }
    }
}

setTimeout(fetch_api_data, 400);
