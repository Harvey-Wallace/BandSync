import React, { useState, useRef } from 'react';
import { 
  Card, 
  CardBody, 
  CardHeader, 
  CardTitle,
  Row,
  Col,
  Button,
  Form,
  FormGroup,
  Input,
  Label,
  Table,
  Alert,
  Modal,
  ModalHeader,
  ModalBody,
  ModalFooter,
  Spinner,
  Nav,
  NavItem,
  NavLink,
  TabContent,
  TabPane,
  Progress,
  Badge
} from 'reactstrap';
import { 
  FaUpload, 
  FaDownload, 
  FaUsers, 
  FaCalendarAlt, 
  FaFileImport,
  FaFileExport,
  FaCheck,
  FaPlus
} from 'react-icons/fa';
import Toast from './Toast';

const BulkOperations = () => {
  const [activeTab, setActiveTab] = useState('import');
  const [importPreview, setImportPreview] = useState(null);
  const [importLoading, setImportLoading] = useState(false);
  const [showPreviewModal, setShowPreviewModal] = useState(false);
  const [showRecurringModal, setShowRecurringModal] = useState(false);
  const [toast, setToast] = useState(null);
  const fileInputRef = useRef(null);

  const [recurringEventForm, setRecurringEventForm] = useState({
    name: '',
    description: '',
    start_datetime: '',
    end_datetime: '',
    location: '',
    recurrence_type: 'weekly',
    recurrence_count: 4,
    rsvp_required: true
  });

  const [exportOptions, setExportOptions] = useState({
    type: 'members',
    start_date: '',
    end_date: '',
    format: 'csv'
  });

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setImportLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/bulk/import/members/preview', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (response.ok) {
        const data = await response.json();
        setImportPreview(data);
        setShowPreviewModal(true);
      } else {
        const error = await response.json();
        setToast({ type: 'error', message: error.error || 'Failed to preview import' });
      }
    } catch (error) {
      setToast({ type: 'error', message: 'Network error during import preview' });
    } finally {
      setImportLoading(false);
    }
  };

  const handleImportMembers = async () => {
    if (!importPreview || importPreview.valid_rows.length === 0) {
      setToast({ type: 'error', message: 'No valid rows to import' });
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/bulk/import/members', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ members: importPreview.valid_data })
      });

      if (response.ok) {
        const data = await response.json();
        setToast({ type: 'success', message: data.message });
        setShowPreviewModal(false);
        setImportPreview(null);
        if (fileInputRef.current) fileInputRef.current.value = '';
      } else {
        const error = await response.json();
        setToast({ type: 'error', message: error.error || 'Failed to import members' });
      }
    } catch (error) {
      setToast({ type: 'error', message: 'Network error during import' });
    }
  };

  const handleExportData = async () => {
    try {
      const token = localStorage.getItem('token');
      const endpoint = exportOptions.type === 'members' ? 
        '/api/bulk/export/members' : 
        `/api/bulk/export/events?start_date=${exportOptions.start_date}&end_date=${exportOptions.end_date}`;

      const response = await fetch(endpoint, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        downloadCSV(data.data, data.filename);
        setToast({ type: 'success', message: 'Data exported successfully' });
      } else {
        const error = await response.json();
        setToast({ type: 'error', message: error.error || 'Failed to export data' });
      }
    } catch (error) {
      setToast({ type: 'error', message: 'Network error during export' });
    }
  };

  const handleCreateRecurringEvents = async (e) => {
    e.preventDefault();
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/bulk/events/recurring', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(recurringEventForm)
      });

      if (response.ok) {
        const data = await response.json();
        setToast({ type: 'success', message: data.message });
        setShowRecurringModal(false);
        setRecurringEventForm({
          name: '',
          description: '',
          start_datetime: '',
          end_datetime: '',
          location: '',
          recurrence_type: 'weekly',
          recurrence_count: 4,
          rsvp_required: true
        });
      } else {
        const error = await response.json();
        setToast({ type: 'error', message: error.error || 'Failed to create recurring events' });
      }
    } catch (error) {
      setToast({ type: 'error', message: 'Network error creating events' });
    }
  };

  const downloadCSV = (data, filename) => {
    if (data.length === 0) return;
    
    const headers = Object.keys(data[0]);
    const csvContent = [
      headers.join(','),
      ...data.map(row => headers.map(header => `"${row[header] || ''}"`).join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const downloadTemplate = () => {
    const template = [
      ['email', 'first_name', 'last_name', 'phone', 'role', 'section', 'instrument'],
      ['member1@example.com', 'John', 'Doe', '555-1234', 'Member', 'Trumpet', 'Trumpet'],
      ['member2@example.com', 'Jane', 'Smith', '555-5678', 'Member', 'Flute', 'Flute'],
      ['admin@example.com', 'Admin', 'User', '555-9999', 'Admin', '', '']
    ];

    const csvContent = template.map(row => row.join(',')).join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', 'member_import_template.csv');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="bulk-operations">
      <Card>
        <CardHeader>
          <CardTitle>
            <FaFileImport className="me-2" />Bulk Operations
          </CardTitle>
        </CardHeader>
        <CardBody>
          <Nav tabs>
            <NavItem>
              <NavLink 
                active={activeTab === 'import'} 
                onClick={() => setActiveTab('import')}
                style={{ cursor: 'pointer' }}
              >
                <FaUpload className="me-2" />Import
              </NavLink>
            </NavItem>
            <NavItem>
              <NavLink 
                active={activeTab === 'export'} 
                onClick={() => setActiveTab('export')}
                style={{ cursor: 'pointer' }}
              >
                <FaDownload className="me-2" />Export
              </NavLink>
            </NavItem>
            <NavItem>
              <NavLink 
                active={activeTab === 'events'} 
                onClick={() => setActiveTab('events')}
                style={{ cursor: 'pointer' }}
              >
                <FaCalendarAlt className="me-2" />Events
              </NavLink>
            </NavItem>
          </Nav>

          <TabContent activeTab={activeTab}>
            {/* Import Tab */}
            <TabPane tabId="import">
              <div className="mt-4">
                <Row>
                  <Col md="6">
                    <Card>
                      <CardHeader>
                        <CardTitle><FaUsers className="me-2" />Member Import</CardTitle>
                      </CardHeader>
                      <CardBody>
                        <p>Import members from a CSV file. Download the template to get started.</p>
                        
                        <div className="mb-3">
                          <Button 
                            color="info" 
                            size="sm" 
                            onClick={downloadTemplate}
                            className="me-2"
                          >
                            <FaDownload className="me-1" />Download Template
                          </Button>
                        </div>

                        <FormGroup>
                          <Label>Select CSV File</Label>
                          <Input
                            type="file"
                            accept=".csv"
                            onChange={handleFileUpload}
                            ref={fileInputRef}
                            disabled={importLoading}
                          />
                          <small className="text-muted">
                            Required columns: email, first_name, last_name<br />
                            Optional columns: phone, role, section, instrument
                          </small>
                        </FormGroup>

                        {importLoading && (
                          <div className="text-center mt-3">
                            <Spinner color="primary" />
                            <p className="mt-2">Processing file...</p>
                          </div>
                        )}
                      </CardBody>
                    </Card>
                  </Col>

                  <Col md="6">
                    <Card>
                      <CardHeader>
                        <CardTitle>Import Guidelines</CardTitle>
                      </CardHeader>
                      <CardBody>
                        <Alert color="info">
                          <strong>Required Fields:</strong>
                          <ul className="mb-0">
                            <li>email (unique identifier)</li>
                            <li>first_name</li>
                            <li>last_name</li>
                          </ul>
                        </Alert>
                        
                        <Alert color="warning">
                          <strong>Optional Fields:</strong>
                          <ul className="mb-0">
                            <li>phone</li>
                            <li>role (Admin or Member)</li>
                            <li>section</li>
                            <li>instrument</li>
                          </ul>
                        </Alert>

                        <Alert color="success">
                          <strong>Tips:</strong>
                          <ul className="mb-0">
                            <li>Use the template for proper formatting</li>
                            <li>Existing users will be added to the organization</li>
                            <li>New users will be created with temporary passwords</li>
                            <li>Preview before importing</li>
                          </ul>
                        </Alert>
                      </CardBody>
                    </Card>
                  </Col>
                </Row>
              </div>
            </TabPane>

            {/* Export Tab */}
            <TabPane tabId="export">
              <div className="mt-4">
                <Row>
                  <Col md="6">
                    <Card>
                      <CardHeader>
                        <CardTitle><FaFileExport className="me-2" />Data Export</CardTitle>
                      </CardHeader>
                      <CardBody>
                        <Form>
                          <FormGroup>
                            <Label>Export Type</Label>
                            <Input
                              type="select"
                              value={exportOptions.type}
                              onChange={(e) => setExportOptions({...exportOptions, type: e.target.value})}
                            >
                              <option value="members">Organization Members</option>
                              <option value="events">Events</option>
                            </Input>
                          </FormGroup>

                          {exportOptions.type === 'events' && (
                            <>
                              <FormGroup>
                                <Label>Start Date</Label>
                                <Input
                                  type="date"
                                  value={exportOptions.start_date}
                                  onChange={(e) => setExportOptions({...exportOptions, start_date: e.target.value})}
                                />
                              </FormGroup>
                              
                              <FormGroup>
                                <Label>End Date</Label>
                                <Input
                                  type="date"
                                  value={exportOptions.end_date}
                                  onChange={(e) => setExportOptions({...exportOptions, end_date: e.target.value})}
                                />
                              </FormGroup>
                            </>
                          )}

                          <FormGroup>
                            <Label>Format</Label>
                            <Input
                              type="select"
                              value={exportOptions.format}
                              onChange={(e) => setExportOptions({...exportOptions, format: e.target.value})}
                            >
                              <option value="csv">CSV</option>
                            </Input>
                          </FormGroup>

                          <Button 
                            color="primary" 
                            onClick={handleExportData}
                          >
                            <FaDownload className="me-1" />Export Data
                          </Button>
                        </Form>
                      </CardBody>
                    </Card>
                  </Col>

                  <Col md="6">
                    <Card>
                      <CardHeader>
                        <CardTitle>Export Information</CardTitle>
                      </CardHeader>
                      <CardBody>
                        <Alert color="info">
                          <strong>Member Export includes:</strong>
                          <ul className="mb-0">
                            <li>Email addresses</li>
                            <li>Names and phone numbers</li>
                            <li>Organization roles</li>
                            <li>Join dates and activity status</li>
                          </ul>
                        </Alert>

                        <Alert color="info">
                          <strong>Event Export includes:</strong>
                          <ul className="mb-0">
                            <li>Event details and descriptions</li>
                            <li>Dates, times, and locations</li>
                            <li>RSVP requirements and deadlines</li>
                            <li>Attendance statistics</li>
                          </ul>
                        </Alert>
                      </CardBody>
                    </Card>
                  </Col>
                </Row>
              </div>
            </TabPane>

            {/* Events Tab */}
            <TabPane tabId="events">
              <div className="mt-4">
                <Row>
                  <Col md="12">
                    <Card>
                      <CardHeader>
                        <CardTitle className="d-flex justify-content-between align-items-center">
                          <span><FaCalendarAlt className="me-2" />Bulk Event Operations</span>
                          <Button 
                            color="primary"
                            onClick={() => setShowRecurringModal(true)}
                          >
                            <FaPlus className="me-1" />Create Recurring Events
                          </Button>
                        </CardTitle>
                      </CardHeader>
                      <CardBody>
                        <Alert color="info">
                          <strong>Recurring Events:</strong> Create multiple events with regular intervals (daily, weekly, or monthly).
                          Perfect for rehearsals, lessons, or regular meetings.
                        </Alert>
                        
                        <Alert color="warning">
                          <strong>Coming Soon:</strong> 
                          <ul className="mb-0">
                            <li>Bulk event editing</li>
                            <li>Event template system</li>
                            <li>Mass event deletion</li>
                            <li>Event series management</li>
                          </ul>
                        </Alert>
                      </CardBody>
                    </Card>
                  </Col>
                </Row>
              </div>
            </TabPane>
          </TabContent>
        </CardBody>
      </Card>

      {/* Import Preview Modal */}
      <Modal isOpen={showPreviewModal} toggle={() => setShowPreviewModal(false)} size="lg">
        <ModalHeader toggle={() => setShowPreviewModal(false)}>
          Import Preview
        </ModalHeader>
        <ModalBody>
          {importPreview && (
            <div>
              <Alert color="info">
                <Row>
                  <Col md="3">
                    <strong>Total Rows:</strong> {importPreview.total_rows}
                  </Col>
                  <Col md="3">
                    <strong>Valid:</strong> <Badge color="success">{importPreview.valid_rows}</Badge>
                  </Col>
                  <Col md="3">
                    <strong>Invalid:</strong> <Badge color="danger">{importPreview.invalid_rows}</Badge>
                  </Col>
                  <Col md="3">
                    <Progress 
                      value={(importPreview.valid_rows / importPreview.total_rows) * 100} 
                      color="success" 
                    />
                  </Col>
                </Row>
              </Alert>

              {importPreview.invalid_data.length > 0 && (
                <div className="mb-3">
                  <h6 className="text-danger">Errors Found:</h6>
                  <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
                    <Table size="sm">
                      <thead>
                        <tr>
                          <th>Row</th>
                          <th>Email</th>
                          <th>Name</th>
                          <th>Errors</th>
                        </tr>
                      </thead>
                      <tbody>
                        {importPreview.invalid_data.map((row, index) => (
                          <tr key={index}>
                            <td>{row.row_number}</td>
                            <td>{row.email}</td>
                            <td>{row.first_name} {row.last_name}</td>
                            <td>
                              {row.errors.map((error, i) => (
                                <Badge key={i} color="danger" className="me-1">
                                  {error}
                                </Badge>
                              ))}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </Table>
                  </div>
                </div>
              )}

              {importPreview.valid_data.length > 0 && (
                <div>
                  <h6 className="text-success">Valid Records (first 10):</h6>
                  <Table size="sm">
                    <thead>
                      <tr>
                        <th>Email</th>
                        <th>Name</th>
                        <th>Role</th>
                        <th>Section</th>
                      </tr>
                    </thead>
                    <tbody>
                      {importPreview.valid_data.slice(0, 10).map((row, index) => (
                        <tr key={index}>
                          <td>{row.email}</td>
                          <td>{row.first_name} {row.last_name}</td>
                          <td>{row.role}</td>
                          <td>{row.section}</td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                </div>
              )}
            </div>
          )}
        </ModalBody>
        <ModalFooter>
          <Button color="secondary" onClick={() => setShowPreviewModal(false)}>
            Cancel
          </Button>
          <Button 
            color="primary" 
            onClick={handleImportMembers}
            disabled={!importPreview || importPreview.valid_rows === 0}
          >
            <FaCheck className="me-1" />Import {importPreview?.valid_rows || 0} Members
          </Button>
        </ModalFooter>
      </Modal>

      {/* Recurring Events Modal */}
      <Modal isOpen={showRecurringModal} toggle={() => setShowRecurringModal(false)}>
        <Form onSubmit={handleCreateRecurringEvents}>
          <ModalHeader toggle={() => setShowRecurringModal(false)}>
            Create Recurring Events
          </ModalHeader>
          <ModalBody>
            <FormGroup>
              <Label>Event Name</Label>
              <Input
                type="text"
                value={recurringEventForm.name}
                onChange={(e) => setRecurringEventForm({...recurringEventForm, name: e.target.value})}
                required
                placeholder="Weekly Rehearsal"
              />
            </FormGroup>

            <FormGroup>
              <Label>Description</Label>
              <Input
                type="textarea"
                value={recurringEventForm.description}
                onChange={(e) => setRecurringEventForm({...recurringEventForm, description: e.target.value})}
                rows={3}
                placeholder="Optional event description"
              />
            </FormGroup>

            <Row>
              <Col md="6">
                <FormGroup>
                  <Label>Start Date & Time</Label>
                  <Input
                    type="datetime-local"
                    value={recurringEventForm.start_datetime}
                    onChange={(e) => setRecurringEventForm({...recurringEventForm, start_datetime: e.target.value})}
                    required
                  />
                </FormGroup>
              </Col>
              <Col md="6">
                <FormGroup>
                  <Label>End Date & Time</Label>
                  <Input
                    type="datetime-local"
                    value={recurringEventForm.end_datetime}
                    onChange={(e) => setRecurringEventForm({...recurringEventForm, end_datetime: e.target.value})}
                  />
                </FormGroup>
              </Col>
            </Row>

            <FormGroup>
              <Label>Location</Label>
              <Input
                type="text"
                value={recurringEventForm.location}
                onChange={(e) => setRecurringEventForm({...recurringEventForm, location: e.target.value})}
                placeholder="Event location"
              />
            </FormGroup>

            <Row>
              <Col md="6">
                <FormGroup>
                  <Label>Recurrence</Label>
                  <Input
                    type="select"
                    value={recurringEventForm.recurrence_type}
                    onChange={(e) => setRecurringEventForm({...recurringEventForm, recurrence_type: e.target.value})}
                  >
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                  </Input>
                </FormGroup>
              </Col>
              <Col md="6">
                <FormGroup>
                  <Label>Number of Events</Label>
                  <Input
                    type="number"
                    value={recurringEventForm.recurrence_count}
                    onChange={(e) => setRecurringEventForm({...recurringEventForm, recurrence_count: parseInt(e.target.value)})}
                    min="1"
                    max="52"
                    required
                  />
                </FormGroup>
              </Col>
            </Row>

            <FormGroup check>
              <Input
                type="checkbox"
                checked={recurringEventForm.rsvp_required}
                onChange={(e) => setRecurringEventForm({...recurringEventForm, rsvp_required: e.target.checked})}
              />
              <Label check>
                Require RSVP for all events
              </Label>
            </FormGroup>
          </ModalBody>
          <ModalFooter>
            <Button color="secondary" onClick={() => setShowRecurringModal(false)}>
              Cancel
            </Button>
            <Button color="primary" type="submit">
              Create {recurringEventForm.recurrence_count} Events
            </Button>
          </ModalFooter>
        </Form>
      </Modal>

      {toast && (
        <Toast
          type={toast.type}
          message={toast.message}
          onClose={() => setToast(null)}
        />
      )}
    </div>
  );
};

export default BulkOperations;
