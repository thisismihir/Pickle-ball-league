function getAuthHeaders() {
    const token = localStorage.getItem("token");

    return {
        "Content-Type": "application/json",
        ...(token && { "Authorization": `Bearer ${token}` })
    };
}

async function apiRequest(endpoint, options = {}) {
    try {
        const response = await fetch(
            `${window.API_BASE_URL || "http://64.227.184.118:8000"}${endpoint}`,
            {
                ...options,
                headers: getAuthHeaders(),
            }
        );

        // Handle unauthorized
        if (response.status === 401) {
            localStorage.removeItem("token");
            localStorage.removeItem("user");
            window.location.href = "login.html";
            throw new Error("Unauthorized");
        }

        // Handle errors
        if (!response.ok) {
            const errorData = await response
                .json()
                .catch(() => ({ detail: "Unknown error" }));

            console.error("API Error Response:", errorData);

            // Handle validation errors (422)
            if (errorData.detail && Array.isArray(errorData.detail)) {
                const errors = errorData.detail
                    .map(err => `${err.loc.join(".")} - ${err.msg}`)
                    .join("; ");
                throw new Error(errors);
            }

            throw new Error(errorData.detail || `HTTP ${response.status}`);
        }

        return response;

    } catch (error) {
        if (error.message === "Unauthorized") {
            throw error;
        }

        console.error("API Request failed:", error);
        throw new Error(error.message || "Failed to fetch");
    }
}

const api = {

    // ================= AUTH =================

    async login(username, password) {
        const response = await fetch(
            `${window.API_BASE_URL || "http://64.227.184.118:8000"}/api/auth/login`,
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password }),
            }
        );
        return response.json();
    },

    async register(username, email, password) {
        const response = await fetch(
            `${window.API_BASE_URL || "http://64.227.184.118:8000"}/api/auth/register`,
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    username,
                    email,
                    password,
                    role: "team_manager"
                }),
            }
        );
        return response.json();
    },

    // ================= TEAMS =================

    async getTeams(includePending = false) {
        const response = await apiRequest(
            `/api/teams?include_pending=${includePending}`
        );
        return response.json();
    },

    async getTeam(teamId) {
        const response = await apiRequest(`/api/teams/${teamId}`);
        return response.json();
    },

    async createTeam(teamData) {
        const response = await apiRequest("/api/teams", {
            method: "POST",
            body: JSON.stringify(teamData),
        });
        return response.json();
    },

    async registerTeam(teamData) {
        const response = await apiRequest("/api/teams", {
            method: "POST",
            body: JSON.stringify(teamData),
        });
        return response.json();
    },

    async approveTeam(teamId, status) {
        const response = await apiRequest(
            `/api/teams/${teamId}/approve`,
            {
                method: "PUT",
                body: JSON.stringify({ status }),
            }
        );
        return response.json();
    },

    // ================= PLAYERS =================

    async createPlayer(playerData) {
        const response = await apiRequest("/api/players", {
            method: "POST",
            body: JSON.stringify(playerData),
        });
        return response.json();
    },

    async registerPlayer(playerData) {
        const response = await apiRequest("/api/players", {
            method: "POST",
            body: JSON.stringify(playerData),
        });
        return response.json();
    },

    async getPlayers(includePending = false, unassignedOnly = false) {
        const response = await apiRequest(
            `/api/players?include_pending=${includePending}&unassigned_only=${unassignedOnly}`
        );
        return response.json();
    },

    async approvePlayer(playerId, status) {
        const response = await apiRequest(
            `/api/players/${playerId}/approve`,
            {
                method: "PUT",
                body: JSON.stringify({ status }),
            }
        );
        return response.json();
    },

    async assignPlayer(playerId, teamId) {
        const response = await apiRequest(
            `/api/players/${playerId}/assign`,
            {
                method: "POST",
                body: JSON.stringify({ team_id: teamId }),
            }
        );
        return response.json();
    },

    // ================= FIXTURES =================

    async getFixtures() {
        const response = await apiRequest("/api/fixtures");
        return response.json();
    },

    async generateFixtures(startDate = null) {
        let url = "/api/fixtures/generate";
        if (startDate) {
            url += `?start_date=${startDate}`;
        }
        const response = await apiRequest(url, {
            method: "POST",
        });
        return response.json();
    },

    async deleteFixtures() {
        const response = await apiRequest("/api/fixtures", {
            method: "DELETE",
        });
        return response;
    },

    // ================= MATCHES =================

    async submitScore(fixtureId, sets, matchDate = null) {
        console.log("===== API.submitScore CALLED =====");
        console.log("fixtureId:", fixtureId);
        console.log("sets parameter:", sets);
        console.log("matchDate:", matchDate);
        console.log("sets type:", typeof sets);
        console.log("sets length:", sets?.length);

        const payload = { sets };
        if (matchDate) {
            payload.match_date = matchDate;
        }
        const payloadString = JSON.stringify(payload);

        console.log("payload object:", payload);
        console.log("payload JSON string:", payloadString);
        console.log("payload string length:", payloadString.length);

        const response = await apiRequest(
            `/api/matches/${fixtureId}/submit-score`,
            {
                method: "POST",
                body: payloadString,
            }
        );

        const result = await response.json();
        console.log("API response:", result);
        console.log("Response set_data:", result.set_data);
        console.log("===== API.submitScore COMPLETE =====");

        return result;
    },

    async confirmScore(fixtureId, sets, matchDate = null) {
        const payload = { sets };
        if (matchDate) {
            payload.match_date = matchDate;
        }
        const response = await apiRequest(
            `/api/matches/${fixtureId}/confirm-score`,
            {
                method: "PUT",
                body: JSON.stringify(payload),
            }
        );
        return response.json();
    },

    async resetScore(fixtureId) {
        const response = await apiRequest(
            `/api/matches/${fixtureId}/reset-score`,
            {
                method: "DELETE",
            }
        );
        return response.json();
    },

    // ================= STANDINGS =================

    async getStandings() {
        const response = await fetch(
            `${window.API_BASE_URL || "http://64.227.184.118:8000"}/api/standings`
        );
        return response.json();
    },

    // ================= ADMIN =================

    async resetTournament() {
        const response = await apiRequest("/api/admin/reset-tournament", {
            method: "DELETE",
        });
        return response.json();
    },
};