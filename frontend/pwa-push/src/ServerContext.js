import React, { createContext, useContext, useEffect, useState } from "react";

const ServerContext = createContext(null);

const DEFAULT_INFO = {
    name: "PDL",
    short_name: "PDL",
    description: "Painel do servidor Lineage 2.",
    version: "1.0",
    chronicle: "",
    logo_url: "/static/pwa/icons/logo.png",
    discord_url: "",
    youtube_url: "",
    facebook_url: "",
    instagram_url: "",
    theme_color: "#0d0d0d",
    rates: {},
    features: {},
};

export function ServerProvider({ children }) {
    const [info, setInfo] = useState(DEFAULT_INFO);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        let cancelled = false;
        fetch("/api/v1/server/info/")
            .then((r) => r.ok ? r.json() : null)
            .then((data) => {
                if (!cancelled && data) setInfo({ ...DEFAULT_INFO, ...data });
            })
            .catch(() => { })
            .finally(() => { if (!cancelled) setLoading(false); });
        return () => { cancelled = true; };
    }, []);

    return (
        <ServerContext.Provider value={{ info, loading }}>
            {children}
        </ServerContext.Provider>
    );
}

export function useServer() {
    return useContext(ServerContext);
}
