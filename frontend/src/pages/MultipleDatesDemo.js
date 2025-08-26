import React, { useState } from 'react';
import { Container, Row, Col, Card, CardBody, CardHeader, Button, Nav, NavItem, NavLink, TabContent, TabPane } from 'reactstrap';
import { Calendar, Vote, Settings } from 'lucide-react';
import MultipleDateEventForm from '../components/MultipleDateEventForm';
import EventDateVoting from '../components/EventDateVoting';

const MultipleDatesDemo = () => {
  const [activeTab, setActiveTab] = useState('create');
  const [testEventId, setTestEventId] = useState(null);
  const [isAdmin, setIsAdmin] = useState(true);

  const toggle = (tab) => {
    if (activeTab !== tab) setActiveTab(tab);
  };

  const handleEventCreated = (event) => {
    console.log('Event created:', event);
    setTestEventId(event.id);
    setActiveTab('vote');
  };

  return (
    <Container className="py-4">
      <Row>
        <Col>
          <Card>
            <CardHeader>
              <h3 className="mb-0">
                <Calendar className="me-2" size={24} />
                Multiple Dates Feature Demo
              </h3>
              <p className="mb-0 mt-2 text-muted">
                Test the new multiple date selection and voting functionality
              </p>
            </CardHeader>
            <CardBody>
              <Nav tabs className="mb-4">
                <NavItem>
                  <NavLink
                    className={activeTab === 'create' ? 'active' : ''}
                    onClick={() => toggle('create')}
                    style={{ cursor: 'pointer' }}
                  >
                    <Settings size={16} className="me-1" />
                    Create Event
                  </NavLink>
                </NavItem>
                <NavItem>
                  <NavLink
                    className={activeTab === 'vote' ? 'active' : ''}
                    onClick={() => toggle('vote')}
                    style={{ cursor: 'pointer' }}
                    disabled={!testEventId}
                  >
                    <Vote size={16} className="me-1" />
                    Vote on Dates
                  </NavLink>
                </NavItem>
              </Nav>

              <TabContent activeTab={activeTab}>
                <TabPane tabId="create">
                  <Row>
                    <Col md="8" className="mx-auto">
                      <MultipleDateEventForm 
                        onEventCreated={handleEventCreated}
                      />
                    </Col>
                  </Row>
                </TabPane>
                
                <TabPane tabId="vote">
                  {testEventId ? (
                    <Row>
                      <Col md="8" className="mx-auto">
                        <div className="mb-3 d-flex justify-content-between align-items-center">
                          <h5>Vote on Event Dates</h5>
                          <div>
                            <Button
                              color={isAdmin ? "primary" : "outline-primary"}
                              size="sm"
                              onClick={() => setIsAdmin(true)}
                              className="me-2"
                            >
                              Admin View
                            </Button>
                            <Button
                              color={!isAdmin ? "primary" : "outline-primary"}
                              size="sm"
                              onClick={() => setIsAdmin(false)}
                            >
                              Member View
                            </Button>
                          </div>
                        </div>
                        
                        <EventDateVoting 
                          eventId={testEventId}
                          isAdmin={isAdmin}
                          onVoteUpdate={() => console.log('Votes updated')}
                          onDateSelected={(dateId) => console.log('Final date selected:', dateId)}
                        />
                      </Col>
                    </Row>
                  ) : (
                    <div className="text-center py-5">
                      <Calendar size={48} className="text-muted mb-3" />
                      <h5>No Event Selected</h5>
                      <p className="text-muted">Create an event with multiple dates first to test the voting functionality.</p>
                      <Button color="primary" onClick={() => setActiveTab('create')}>
                        Create Test Event
                      </Button>
                    </div>
                  )}
                </TabPane>
              </TabContent>
            </CardBody>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default MultipleDatesDemo;
