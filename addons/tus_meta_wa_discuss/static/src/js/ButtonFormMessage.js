/** @odoo-module **/

const { Component, tags, hooks} = owl;
const { useState } = hooks;
const { useRef } = owl.hooks;
const rpc = require('web.rpc');
var ajax = require('web.ajax');

export class ButtonFormMessage extends Component {
    static props = {
        partnerData: Object,  
    };
    counter1 = useState({ value: 0 ,});
    mobile = useState({ value: '' });

    constructor(WaThreadView) {
            super(...arguments);
            var self=this;
            this.WaThreadView = WaThreadView

            // console.log("Received partnerData in ButtonFormMessage:", this.props.partnerData);
            const partnerId = this.props.partnerData.id; 

            self.users = []
            self.agents = []
            rpc.query({
                model: 'res.partner',
                method: 'read',
                args: [[partnerId], ['mobile']],
            }).then(function (result) {
                if (result.length > 0) {
                    // console.log("Nomor Telepon Partner:", result[0].mobile);
                    self.mobile.value = result[0].mobile; 
                }
            });
    
            rpc.query({
                model: 'mail.channel',
                method: 'get_channel_agent',
                args: [[], partnerId],  
            }).then(function (result) {
                $('#main-button').addClass('o_hidden');
                self.users = result['users'];
                self.agents = result['channel_users'];
                self.counter1.value++;
            });
        }

    async sendMessage(template_name) {
        const nomor = this.mobile.value;
        const url = "https://graph.facebook.com/v21.0/426469107220591/messages";
        const access_token = "EAAOT6dJD7ZBMBOzdC9eranvzlc4SbFM5RmZCIsKaKyWMKNFZBqmPHQNTZAMop4WcjPMOyuNl8tAlBsM9zi6S5LG7Jys58HXPvqXcMbndmP0mlcBHJz6o3lKKFGmI5CTbWo3o3ZBpN6cqEjbLYUmII2U0LZAshv48ZAiSNKKaXzlZAXY13oCkYBtEEk8JkHaZCbWPskgZDZD";

        const payload = {
            messaging_product: "whatsapp",
            to: nomor,
            type: "template",
            template: {
                name: template_name,
                language: { code: "en_US" },
                components: [
                    { type: "body" },
                    { type: "button", sub_type: "flow", index: 0 }
                ]
            }
        };

        try {
            let response = await fetch(url, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${access_token}`,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            let result = await response.json();
            if (response.ok) {
                console.log("WhatsApp message sent successfully:", result);
            } else {
                console.error("Failed to send WhatsApp message:", result);
            }
        } catch (error) {
            console.error("Error sending WhatsApp message:", error);
        }
    }
}
