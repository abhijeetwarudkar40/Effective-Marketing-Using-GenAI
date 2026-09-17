import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from './components/layout/AppLayout';
import { DashboardPage } from './pages/DashboardPage';
import { CustomersPage } from './pages/CustomersPage';
import { SegmentsPage } from './pages/SegmentsPage';
import { RecommendationsPage } from './pages/RecommendationsPage';
import { CampaignStudioPage } from './pages/CampaignStudioPage';
import { CreativeStudioPage } from './pages/CreativeStudioPage';
import { CompliancePage } from './pages/CompliancePage';
import { DeliveryPage } from './pages/DeliveryPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { GovernancePage } from './pages/GovernancePage';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppLayout />}>
          <Route index element={<DashboardPage />} />
          <Route path="customers" element={<CustomersPage />} />
          <Route path="segments" element={<SegmentsPage />} />
          <Route path="recommendations" element={<RecommendationsPage />} />
          <Route path="campaign-studio" element={<CampaignStudioPage />} />
          <Route path="creative-studio" element={<CreativeStudioPage />} />
          <Route path="compliance" element={<CompliancePage />} />
          <Route path="delivery" element={<DeliveryPage />} />
          <Route path="analytics" element={<AnalyticsPage />} />
          <Route path="governance" element={<GovernancePage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default App;
