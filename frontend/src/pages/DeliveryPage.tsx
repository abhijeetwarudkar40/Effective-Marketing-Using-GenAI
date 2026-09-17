import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Send,
  Mail,
  MessageSquare,
  CheckCircle2,
  AlertCircle,
  ShieldCheck,
  RefreshCw,
  Image as ImageIcon,
  Palette
} from 'lucide-react';
import { sendEmail, sendSms, getDeliveries, getApprovedCreative } from '../services/api';
import { CampaignContent, DeliveryLog } from '../types';
import { PageHeader } from '../components/common/PageHeader';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { EmptyState } from '../components/common/EmptyState';

export const DeliveryPage: React.FC = () => {
  const navigate = useNavigate();
  const [campaign, setCampaign] = useState<CampaignContent | null>(null);
  const [campaignId, setCampaignId] = useState<number | null>(null);

  // Delivery inputs
  const [channel, setChannel] = useState<'Email' | 'SMS'>('Email');
  const [recipient, setRecipient] = useState('');
  const [sending, setSending] = useState(false);
  const [deliveryResult, setDeliveryResult] = useState<{ status: string; message: string; image_attached?: boolean } | null>(null);

  // Approved creative image
  const [approvedCreativeB64, setApprovedCreativeB64] = useState<string | null>(null);

  // Logs
  const [logs, setLogs] = useState<DeliveryLog[]>([]);
  const [loadingLogs, setLoadingLogs] = useState(false);

  useEffect(() => {
    const storedCampaign = localStorage.getItem('bankwise_active_campaign');
    const storedId = localStorage.getItem('bankwise_active_campaign_id');
    const storedB64 = localStorage.getItem('bankwise_approved_creative_b64');

    if (storedCampaign) {
      try {
        const parsed = JSON.parse(storedCampaign);
        setCampaign(parsed);
        if (storedId) {
          const cid = Number(storedId);
          setCampaignId(cid);
          loadCreative(cid, storedB64);
        }
      } catch (e) {
        console.error(e);
      }
    }
    loadLogs();
  }, []);

  const loadCreative = async (cid: number, fallbackB64: string | null) => {
    if (fallbackB64) {
      setApprovedCreativeB64(fallbackB64);
      return;
    }
    try {
      const res = await getApprovedCreative(cid);
      if (res.has_creative && res.image_base64) {
        setApprovedCreativeB64(res.image_base64);
      }
    } catch (e) {
      console.error('Failed to load approved creative:', e);
    }
  };

  const loadLogs = async () => {
    try {
      setLoadingLogs(true);
      const data = await getDeliveries();
      setLogs(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingLogs(false);
    }
  };

  const handleSend = async () => {
    if (!campaign || !campaignId || !recipient.trim()) return;
    try {
      setSending(true);
      setDeliveryResult(null);

      let res;
      if (channel === 'Email') {
        const imagePayload = approvedCreativeB64 || localStorage.getItem('bankwise_approved_creative_b64') || undefined;
        res = await sendEmail(campaignId, campaign, recipient.trim(), imagePayload);
      } else {
        res = await sendSms(campaignId, campaign, recipient.trim());
      }

      setDeliveryResult(res);
      loadLogs();
    } catch (err: any) {
      setDeliveryResult({
        status: 'FAILED',
        message: err.response?.data?.detail || err.message || 'Delivery request failed.',
      });
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Multi-Channel Campaign Delivery"
        subtitle="Execute high-deliverability email (Gmail SMTP with embedded approved creative banner) and SMS outreach for banking campaigns."
      />

      {!campaign ? (
        <EmptyState
          title="No campaign ready for delivery"
          description="Create and approve a campaign first."
          action={
            <button
              onClick={() => navigate('/campaign-studio')}
              className="bg-[#00A896] text-white px-4 py-2 rounded-lg text-xs font-semibold hover:bg-[#008f80] transition-colors"
            >
              Go to Campaign Studio
            </button>
          }
        />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Dispatch Settings Form */}
          <div className="lg:col-span-1 bg-white p-6 rounded-xl border border-gray-200 shadow-xs space-y-5 flex flex-col justify-between">
            <div className="space-y-5">
              <div className="border-b border-gray-100 pb-3 flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-bold text-[#0A1628]">Dispatch Configuration</h3>
                  <p className="text-xs text-gray-500 mt-0.5">Campaign #{campaignId} ready</p>
                </div>
                {approvedCreativeB64 && (
                  <Badge variant="teal" className="flex items-center space-x-1">
                    <ImageIcon className="w-3 h-3 mr-1" />
                    <span>Banner Attached</span>
                  </Badge>
                )}
              </div>

              {/* Channel Selector */}
              <div>
                <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-2">
                  Delivery Channel
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    onClick={() => {
                      setChannel('Email');
                      setDeliveryResult(null);
                    }}
                    className={`py-2.5 px-3 rounded-lg border text-xs font-semibold flex items-center justify-center space-x-2 transition-all ${
                      channel === 'Email'
                        ? 'border-[#00A896] bg-[#00A896]/10 text-[#007A6C]'
                        : 'border-gray-200 text-gray-600 hover:bg-gray-50'
                    }`}
                  >
                    <Mail className="w-4 h-4" />
                    <span>Email Gateway</span>
                  </button>

                  <button
                    onClick={() => {
                      setChannel('SMS');
                      setDeliveryResult(null);
                    }}
                    className={`py-2.5 px-3 rounded-lg border text-xs font-semibold flex items-center justify-center space-x-2 transition-all ${
                      channel === 'SMS'
                        ? 'border-[#00A896] bg-[#00A896]/10 text-[#007A6C]'
                        : 'border-gray-200 text-gray-600 hover:bg-gray-50'
                    }`}
                  >
                    <MessageSquare className="w-4 h-4" />
                    <span>SMS Gateway</span>
                  </button>
                </div>
              </div>

              {/* Recipient Input */}
              <div>
                <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
                  {channel === 'Email' ? 'Recipient Email Address' : 'Recipient Phone Number'}
                </label>
                <input
                  type={channel === 'Email' ? 'email' : 'tel'}
                  placeholder={channel === 'Email' ? 'customer@example.com' : '+91 98765 43210'}
                  value={recipient}
                  onChange={(e) => setRecipient(e.target.value)}
                  className="w-full text-xs border border-gray-300 rounded-lg p-2.5 focus:outline-none focus:ring-2 focus:ring-[#00A896]/20 focus:border-[#00A896]"
                />
                <p className="text-[11px] text-gray-400 mt-1">
                  {channel === 'Email'
                    ? 'Sends via authenticated Gmail SMTP with embedded creative graphic.'
                    : 'Simulated dry-run SMS transmission.'}
                </p>
              </div>

              {/* Creative Banner Indicator */}
              {channel === 'Email' && (
                <div className="p-3 bg-gray-50 rounded-lg border border-gray-200 text-xs">
                  {approvedCreativeB64 ? (
                    <div className="flex items-center space-x-2 text-green-800">
                      <CheckCircle2 className="w-4 h-4 text-green-600 shrink-0" />
                      <span className="font-medium">
                        Approved Creative Studio banner is attached and will be embedded inline in the email.
                      </span>
                    </div>
                  ) : (
                    <div className="flex items-center justify-between text-gray-600">
                      <span>No banner creative approved.</span>
                      <button
                        onClick={() => navigate('/creative-studio')}
                        className="text-[#00A896] hover:underline font-bold text-[11px] flex items-center"
                      >
                        <Palette className="w-3 h-3 mr-1" />
                        <span>Select Banner →</span>
                      </button>
                    </div>
                  )}
                </div>
              )}

              {/* Status Alert */}
              {deliveryResult && (
                <div
                  className={`p-3 rounded-lg text-xs font-medium border flex items-start space-x-2 ${
                    deliveryResult.status === 'SENT' || deliveryResult.status === 'DRY_RUN_SIMULATED'
                      ? 'bg-green-50 text-green-800 border-green-200'
                      : 'bg-red-50 text-red-800 border-red-200'
                  }`}
                >
                  {deliveryResult.status === 'SENT' || deliveryResult.status === 'DRY_RUN_SIMULATED' ? (
                    <CheckCircle2 className="w-4 h-4 text-green-600 shrink-0 mt-0.5" />
                  ) : (
                    <AlertCircle className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />
                  )}
                  <div>
                    <p className="font-bold">{deliveryResult.message}</p>
                    {deliveryResult.image_attached && (
                      <p className="text-[11px] text-green-700 mt-0.5">✓ Inline graphic banner embedded in email message.</p>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Send Button */}
            <button
              onClick={handleSend}
              disabled={sending || !recipient.trim()}
              className="w-full py-3 bg-[#1A3A5C] hover:bg-[#0A1628] text-white font-bold text-xs rounded-lg shadow-sm transition-all flex items-center justify-center space-x-2 disabled:opacity-50 mt-4"
            >
              {sending ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Transmitting Payload...</span>
                </>
              ) : (
                <>
                  <Send className="w-4 h-4 text-[#00A896]" />
                  <span>Send Campaign Now</span>
                </>
              )}
            </button>
          </div>

          {/* Exact Payload Content Preview */}
          <div className="lg:col-span-2 bg-white rounded-xl border border-gray-200 shadow-xs overflow-hidden flex flex-col justify-between">
            <div className="bg-[#0A1628] text-white p-4 flex items-center justify-between">
              <span className="text-xs font-bold tracking-wide">
                Live Outgoing Payload ({channel})
              </span>
              <Badge variant="teal">Exact Template</Badge>
            </div>

            <div className="p-6 overflow-y-auto max-h-[500px]">
              {channel === 'Email' ? (
                /* Email Preview Container */
                <div className="border border-gray-200 rounded-xl max-w-xl mx-auto bg-white shadow-xs overflow-hidden">
                  <div className="bg-gray-50 p-4 border-b border-gray-200 text-xs text-gray-600">
                    <div><strong>Subject:</strong> {campaign.subject || campaign.subject_line}</div>
                    <div className="mt-1"><strong>To:</strong> {recipient || 'customer@example.com'}</div>
                  </div>

                  <div className="p-6 space-y-4 text-xs text-gray-800 leading-relaxed">
                    {campaign.headline && <h3 className="text-lg font-bold text-gray-900">{campaign.headline}</h3>}
                    <p className="font-medium text-gray-700">{campaign.greeting || 'Hello,'}</p>

                    {/* Embedded Approved Creative Banner Image */}
                    {approvedCreativeB64 && (
                      <div className="my-3 rounded-lg overflow-hidden border border-gray-200 shadow-xs">
                        <img
                          src={approvedCreativeB64}
                          alt="Approved marketing banner"
                          className="w-full h-auto block"
                        />
                      </div>
                    )}

                    <p className="whitespace-pre-line">{campaign.email_body || campaign.body}</p>
                    {campaign.cta && (
                      <div className="py-2">
                        <span className="inline-block px-4 py-2 rounded-lg bg-[#1A3A5C] text-white font-bold text-xs">
                          {campaign.cta}
                        </span>
                      </div>
                    )}
                    <p className="text-gray-500 italic whitespace-pre-line mt-4">{campaign.closing || 'Regards,\nYour Banking Team'}</p>
                  </div>

                  <div className="bg-gray-50 p-3 border-t border-gray-200 text-[10px] text-gray-500 text-center">
                    Confidential banking communication · BankWise AI Intelligence
                  </div>
                </div>
              ) : (
                /* SMS Preview Container */
                <div className="max-w-sm mx-auto bg-gray-900 text-white rounded-2xl p-5 shadow-lg border border-gray-800 space-y-3 font-sans">
                  <div className="flex items-center justify-between text-[11px] text-gray-400 border-b border-gray-800 pb-2">
                    <span>SMS Message</span>
                    <span>To: {recipient || '+91 XXXXX XXXXX'}</span>
                  </div>
                  <div className="bg-[#1A3A5C] p-4 rounded-xl text-xs leading-relaxed text-gray-100 font-mono">
                    {campaign.sms || `${campaign.headline} ${campaign.email_body} ${campaign.cta}`}
                  </div>
                  <div className="text-right text-[10px] text-gray-500">
                    Characters: {campaign.sms?.length || 0}
                  </div>
                </div>
              )}
            </div>

            <div className="p-4 bg-gray-50 border-t border-gray-200 text-xs text-gray-500 flex items-center justify-between">
              <span>Security: TLS 1.3 encrypted transmission</span>
              <span>Recipient consent confirmed</span>
            </div>
          </div>
        </div>
      )}

      {/* Historical Delivery Logs Table */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-xs overflow-hidden mt-6">
        <div className="p-4 border-b border-gray-100 flex items-center justify-between">
          <h3 className="text-sm font-bold text-[#0A1628]">Real Delivery Logs (SQLite Audit)</h3>
          <button onClick={loadLogs} className="text-xs text-[#00A896] hover:underline font-semibold flex items-center space-x-1">
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Refresh Logs</span>
          </button>
        </div>

        {loadingLogs ? (
          <LoadingSpinner message="Fetching delivery logs from database..." />
        ) : logs.length === 0 ? (
          <div className="p-8 text-center text-xs text-gray-500">No delivery logs recorded yet.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-gray-50 text-gray-700 border-b border-gray-200 font-semibold">
                  <th className="py-2.5 px-4">Log ID</th>
                  <th className="py-2.5 px-4">Campaign ID</th>
                  <th className="py-2.5 px-4">Channel</th>
                  <th className="py-2.5 px-4">Recipient</th>
                  <th className="py-2.5 px-4">Status</th>
                  <th className="py-2.5 px-4">Provider Message</th>
                  <th className="py-2.5 px-4">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {logs.map((log) => (
                  <tr key={log.id} className="hover:bg-gray-50/80">
                    <td className="py-2.5 px-4 font-mono text-gray-500">#{log.id}</td>
                    <td className="py-2.5 px-4 font-mono font-semibold text-[#1A3A5C]">#{log.campaign_id}</td>
                    <td className="py-2.5 px-4 font-medium">{log.channel}</td>
                    <td className="py-2.5 px-4 font-mono text-gray-600">{log.recipient}</td>
                    <td className="py-2.5 px-4">
                      <Badge variant={log.status === 'SENT' || log.status === 'DRY_RUN_SIMULATED' ? 'success' : 'danger'}>
                        {log.status}
                      </Badge>
                    </td>
                    <td className="py-2.5 px-4 text-gray-600 max-w-xs truncate">{log.provider_message}</td>
                    <td className="py-2.5 px-4 text-gray-400 font-mono text-[11px]">
                      {new Date(log.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
