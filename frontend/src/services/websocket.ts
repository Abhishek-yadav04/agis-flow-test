

class WebSocketService {
  private socket: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private baseReconnectDelay = 1000;
  private listeners: Map<string, Set<(data: any) => void>> = new Map();
  private heartbeatIntervalMs = 15000;
  private heartbeatTimeoutMs = 12000; // time to wait for pong
  private heartbeatTimer: any = null;
  private pongTimeout: any = null;
  private manualClose = false;

  connect(): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      return;
    }

  this.manualClose = false;

    const token = localStorage.getItem('auth_token');
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const url = `${protocol}//${host}/ws${token ? `?token=${encodeURIComponent(token)}` : ''}`;
  this.socket = new WebSocket(url);

    this.setupEventHandlers();
  }

  private setupEventHandlers(): void {
    if (!this.socket) return;

    this.socket.onopen = () => {
      this.reconnectAttempts = 0;
      this.emit('connection', { status: 'connected' });
      this.startHeartbeat();
    };

    this.socket.onclose = (ev) => {
      this.clearHeartbeat();
      this.emit('connection', { status: 'disconnected', reason: ev.reason });
      if (!this.manualClose) this.handleReconnect();
    };

    this.socket.onerror = (ev) => {
      this.emit('connection', { status: 'error', error: String(ev) });
      // Let close event trigger reconnect to avoid double attempts
    };

    this.socket.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data);
        const type = msg.type || 'message';
        this.emit(type, msg);
      } catch (e) {
        // Non-JSON payloads ignored
      }
    };
  }

  private handleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      return;
    }
    this.reconnectAttempts++;
    const exp = Math.pow(2, this.reconnectAttempts - 1);
    const jitter = 300 + Math.random() * 300;
    const delay = this.baseReconnectDelay * exp + jitter;
    setTimeout(() => {
      console.log(`Reconnecting attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts} after ${Math.round(delay)}ms`);
      this.connect();
    }, delay);
  }

  private startHeartbeat() {
    this.clearHeartbeat();
    this.heartbeatTimer = setInterval(() => {
      if (!this.socket || this.socket.readyState !== WebSocket.OPEN) return;
      try {
        this.socket.send(JSON.stringify({ type: 'ping', ts: Date.now() }));
        if (this.pongTimeout) clearTimeout(this.pongTimeout);
        this.pongTimeout = setTimeout(() => {
          console.warn('Heartbeat pong not received, closing socket to trigger reconnect');
          try { this.socket?.close(); } catch {}
        }, this.heartbeatTimeoutMs);
      } catch (e) {
        console.warn('Heartbeat send failed', e);
      }
    }, this.heartbeatIntervalMs);
  }

  private clearHeartbeat() {
    if (this.heartbeatTimer) clearInterval(this.heartbeatTimer);
    if (this.pongTimeout) clearTimeout(this.pongTimeout);
    this.heartbeatTimer = null;
    this.pongTimeout = null;
  }

  disconnect(): void {
  this.manualClose = true;
  this.clearHeartbeat();
  if (this.socket) try { this.socket.close(); } catch {} finally { this.socket = null; }
    this.listeners.clear();
  }

  on(event: string, callback: (data: any) => void): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(callback);
  }

  off(event: string, callback: (data: any) => void): void {
    const eventListeners = this.listeners.get(event);
    if (eventListeners) {
      eventListeners.delete(callback);
      if (eventListeners.size === 0) {
        this.listeners.delete(event);
      }
    }
  }

  private emit(event: string, data: any): void {
    const eventListeners = this.listeners.get(event);
    if (eventListeners) {
      eventListeners.forEach(callback => callback(data));
    }
  }

  send(event: string, data: any): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({ type: event, data }));
    } else {
      console.warn('WebSocket not connected, cannot send message');
    }
  }

  isConnected(): boolean {
    return this.socket?.readyState === WebSocket.OPEN || false;
  }

  getConnectionState(): string {
    if (!this.socket) return 'disconnected';
    return this.socket.readyState === WebSocket.OPEN ? 'connected' : 'disconnected';
  }
}

export const websocketService = new WebSocketService();
export default websocketService;