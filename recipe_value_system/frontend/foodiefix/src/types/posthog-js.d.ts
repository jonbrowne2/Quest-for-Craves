declare module 'posthog-js' {
  interface PostHogConfig {
    api_host?: string;
    autocapture?: boolean;
    capture_pageview?: boolean;
    disable_session_recording?: boolean;
    property_blacklist?: string[];
    [key: string]: any;
  }

  interface Properties {
    [key: string]: any;
  }

  interface PostHog {
    init(
      apiKey: string,
      config?: Partial<PostHogConfig>
    ): void;

    capture(
      eventName: string,
      properties?: Properties,
      callback?: () => void
    ): void;

    identify(
      distinctId: string,
      properties?: Properties,
      callback?: () => void
    ): void;

    alias(alias: string, distinctId?: string): void;

    people: {
      set(properties: Properties): void;
      set_once(properties: Properties): void;
      increment(property: string | Properties, value?: number): void;
      append(property: string | Properties, value?: any): void;
      union(property: string | Properties, value?: any): void;
      unset(property: string | string[]): void;
      remove(property: string | Properties, value?: any): void;
      delete_user(): void;
    };

    reset(resetDeviceId?: boolean): void;
    debug(enabled?: boolean): void;
    opt_in_capturing(): void;
    opt_out_capturing(): void;
    has_opted_in_capturing(): boolean;
    has_opted_out_capturing(): boolean;
    isFeatureEnabled(key: string): boolean;
    getFeatureFlag(key: string): string | boolean;
    onFeatureFlags(callback: (flags: string[]) => void): void;
    reloadFeatureFlags(): void;
  }

  const posthog: PostHog;
  export = posthog;
}
