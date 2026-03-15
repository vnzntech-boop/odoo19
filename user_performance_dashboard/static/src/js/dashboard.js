/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

class UserPerformanceDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this._settingFilter = false;
        this._lastFetchParams = null;

        const today = new Date();
        const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
        const lastDay = new Date(today.getFullYear(), today.getMonth() + 1, 0);

        this.state = useState({
            user_data: {
                name: "",
                job_title: "",
                image_url: "",
                customer_count: 0,
                payment_amount: "SAR 0.00",
                all_users: [],
            },
            filters: {
                start_date: firstDay.toISOString().split('T')[0],
                end_date: lastDay.toISOString().split('T')[0],
                user_id: null,
            }
        });

        onWillStart(async () => {
            await this._fetch_data();
        });
    }

    async _fetch_data() {
        const params = {
            start_date: this.state.filters.start_date,
            end_date: this.state.filters.end_date,
            target_user_id: parseInt(this.state.filters.user_id) || null,
        };

        try {
            const same = this._lastFetchParams && this._lastFetchParams.start_date === params.start_date && this._lastFetchParams.end_date === params.end_date && this._lastFetchParams.target_user_id === params.target_user_id;
            if (same) {
                return;
            }
        } catch (e) {
            // ignore
        }

        const res = await this.orm.call("user.performance.dashboard", "get_dashboard_data", [], params);
        this.state.user_data = res;
        if (!this.state.filters.user_id) {
            this._settingFilter = true;
            this.state.filters.user_id = res.current_user_id;
            setTimeout(() => { this._settingFilter = false; }, 0);
        }

        this._lastFetchParams = params;
    }

    async _onFilterChange() {
        if (this._settingFilter) {
            return;
        }
        await this._fetch_data();
    }
}

UserPerformanceDashboard.template = "user_performance_dashboard.DashboardTemplate";

registry.category("actions").add("user_performance_dashboard_tag", UserPerformanceDashboard);
