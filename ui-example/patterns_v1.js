const PATTERNS = {
            'C1': {
                name: 'Graph Structure',
                type: 'Concept',
                definition: 'A graph structure represents entities (nodes) and their relationships (edges), fundamental to modeling connected data.',
                components: '\lambda_n, \lambda_e',
                manifestations: 'Knowledge graphs, File trees, Feature history, Axiom dependencies, Part hierarchies'
            },
            'C2': {
                name: 'Document/Artifact',
                type: 'Concept',
                definition: 'Documents and artifacts process input to produce output, encapsulating computational transformation patterns.',
                components: 'input, process, output, display',
                manifestations: 'Document/Artifact in modern applications, Web-based document/artifact, Mobile document/artifact'
            },
            'C3': {
                name: 'Symbolic Expression',
                type: 'Concept',
                definition: 'Symbolic expressions represent mathematical and computational formulas as structured tree data.',
                components: 'root, children',
                manifestations: 'Symbolic math, Tags/taxonomies, Code AST, Mathematical formulas, Constraints'
            },
            'C4': {
                name: 'Metadata Schema',
                type: 'Concept',
                definition: 'Metadata schemas define structured data fields with types and validation rules.',
                components: 'schema, data, validators',
                manifestations: 'Tags, Properties, Attributes, Annotations, Labels'
            },
            'C5': {
                name: 'Version History',
                type: 'Concept',
                definition: 'Version history tracks changes over time as immutable states and deltas.',
                components: 'states, deltas, branches',
                manifestations: 'Git commits, Document revisions, Database transaction log, Edit history, Feature sequence'
            },
            'F1.1': {
                name: 'Input Capture Flow',
                type: 'Flow',
                definition: 'Input capture validates and normalizes external inputs before storing in the system.',
                components: 'source, validator, normalizer, store',
                manifestations: 'Various applications'
            },
            'F1.2': {
                name: 'Data Import Flow',
                type: 'Flow',
                definition: 'Data import parses external formats and transforms them to internal schema.',
                components: 'source, parser, transformer, integrator',
                manifestations: 'Various applications'
            },
            'F1.3': {
                name: 'Live Data Stream Flow',
                type: 'Flow',
                definition: 'Live data stream processes continuous event flows with buffering and backpressure.',
                components: 'stream, buffer, processor, emitter',
                manifestations: 'Various applications'
            },
            'F2.1': {
                name: 'Processing Pipeline Flow',
                type: 'Flow',
                definition: 'Processing pipelines compose sequential transformation stages with intermediate representations.',
                components: 'stages, ir, error\_handler, compose',
                manifestations: 'Various applications'
            },
            'F2.2': {
                name: 'Transformation Flow',
                type: 'Flow',
                definition: 'Transformation flows convert data from one representation to another through mappings.',
                components: 'agents, coordinator, tasks, results',
                manifestations: 'Various applications'
            },
            'F2.3': {
                name: 'Validation Flow',
                type: 'Flow',
                definition: 'Validation flows check data integrity and business rules at processing boundaries.',
                components: 'graph, cache, invalidate, recompute',
                manifestations: 'Various applications'
            },
            'F2.4': {
                name: 'Enrichment Flow',
                type: 'Flow',
                definition: 'Enrichment flows augment data with additional context from external sources.',
                components: 'base, enrichers, combine, output',
                manifestations: 'Various applications'
            },
            'F3.1': {
                name: 'State Transition Flow',
                type: 'Flow',
                definition: 'State transition flows manage discrete state changes through defined transitions.',
                components: 'observe, learn, update, apply',
                manifestations: 'Various applications'
            },
            'F3.2': {
                name: 'Event-Driven Flow',
                type: 'Flow',
                definition: 'Event-driven flows react to events by dispatching handlers and updating state.',
                components: 'validate, report, correct, verify',
                manifestations: 'Various applications'
            },
            'F3.3': {
                name: 'Adaptation Loop Flow',
                type: 'Flow',
                definition: 'Adaptation loops monitor system behavior and adjust parameters dynamically.',
                components: 'monitor, detect, adjust, measure',
                manifestations: 'Various applications'
            },
            'F3.4': {
                name: 'Feedback Loop Flow',
                type: 'Flow',
                definition: 'Feedback loops use output to adjust input in closed-loop control systems.',
                components: 'track, infer, personalize, apply',
                manifestations: 'Various applications'
            },
            'F4.1': {
                name: 'Presentation Flow',
                type: 'Flow',
                definition: 'Presentation flows prepare and format data for display to users.',
                components: 'state, render, diff, patch',
                manifestations: 'Various applications'
            },
            'F4.2': {
                name: 'Query Flow',
                type: 'Flow',
                definition: 'Query flows retrieve and filter data based on criteria and return results.',
                components: 'trigger, route, format, deliver',
                manifestations: 'Various applications'
            },
            'F4.3': {
                name: 'Export and Publishing Flow',
                type: 'Flow',
                definition: 'Export flows transform internal data to external formats and publish to destinations.',
                components: 'source, transform, validate, publish',
                manifestations: 'Various applications'
            },
            'F4.4': {
                name: 'Synchronization Flow',
                type: 'Flow',
                definition: 'Synchronization flows keep multiple data sources consistent through coordination.',
                components: 'query, compute, cache, refresh',
                manifestations: 'Various applications'
            },
            'P1': {
                name: 'Direct Manipulation Canvas',
                type: 'Pattern',
                definition: 'Direct manipulation canvases enable users to interact with visual objects through direct gestures.',
                components: 'viewport, objects, cursor, tools',
                manifestations: 'Graph editor, 3D viewport, Drawing canvas, Visual editor, Diagram editors'
            },
            'P10': {
                name: 'Parser/Compiler Pipeline',
                type: 'Pattern',
                definition: 'Parser/compiler pipelines transform source code through multiple stages to produce executable output.',
                components: 'input, process, output, display',
                manifestations: 'Parser/Compiler Pipeline in modern applications, Web-based parser/compiler pipeline, Mobile parser/compiler pipeline'
            },
            'P11': {
                name: 'Validator/Checker',
                type: 'Pattern',
                definition: 'Validators check data against rules and constraints to ensure correctness and completeness.',
                components: 'input, process, output, display',
                manifestations: 'Validator/Checker in modern applications, Web-based validator/checker, Mobile validator/checker'
            },
            'P12': {
                name: 'Solver/Optimizer',
                type: 'Pattern',
                definition: 'Solvers and optimizers find optimal solutions to constrained problems using algorithms.',
                components: 'input, process, output, display',
                manifestations: 'Solver/Optimizer in modern applications, Web-based solver/optimizer, Mobile solver/optimizer'
            },
            'P13': {
                name: 'Indexer/Query Engine',
                type: 'Pattern',
                definition: 'Indexers build searchable indexes and query engines retrieve relevant information efficiently.',
                components: 'input, process, output, display',
                manifestations: 'Indexer/Query Engine in modern applications, Web-based indexer/query engine, Mobile indexer/query engine'
            },
            'P14': {
                name: 'Agent Swarm',
                type: 'Pattern',
                definition: 'Agent swarms coordinate multiple AI agents to solve complex problems collaboratively.',
                components: 'agents, tasks, coord, results',
                manifestations: 'Multi-agent reasoning, Parallel analysis, Distributed builds, Map-reduce'
            },
            'P15': {
                name: 'Reasoning Chain',
                type: 'Pattern',
                definition: 'Reasoning chains show step-by-step logical inference and decision-making processes.',
                components: 'steps, state, deps, result',
                manifestations: 'AI reasoning, Proof derivation, Build pipelines, Computation traces'
            },
            'P16': {
                name: 'Suggestion/Recommendation System',
                type: 'Pattern',
                definition: 'Suggestion and recommendation systems analyze context to provide relevant suggestions to users.',
                components: 'input, process, output, display',
                manifestations: 'Suggestion/Recommendation System in modern applications, Web-based suggestion/recommendation system, Mobile suggestion/recommendation system'
            },
            'P17': {
                name: 'Key-Value Store',
                type: 'Pattern',
                definition: 'Key-value stores provide fast access to data using simple key lookups.',
                components: 'store, get, set, delete',
                manifestations: 'Cache, Settings storage, Session state, Metadata store'
            },
            'P18': {
                name: 'Relational Database',
                type: 'Pattern',
                definition: 'Relational databases organize data in tables with relationships and support SQL queries.',
                components: 'tables, schemas, constraints, indices',
                manifestations: 'Content database, File metadata, User data, Application state'
            },
            'P19': {
                name: 'Graph Database',
                type: 'Pattern',
                definition: 'Graph databases store data as nodes and edges optimized for traversing relationships.',
                components: 'nodes, edges, props, traversal',
                manifestations: 'Knowledge graphs, Dependency graphs, Citation networks, Social networks'
            },
            'P2': {
                name: 'Command Interface',
                type: 'Pattern',
                definition: 'Command interfaces enable users to execute actions through text-based commands.',
                components: 'input, parser, executor, history',
                manifestations: 'Search bar, Command line, Command palette, Query input'
            },
            'P20': {
                name: 'Document Store',
                type: 'Pattern',
                definition: 'Document stores save and retrieve semi-structured documents with flexible schemas.',
                components: 'collections, documents, queries, indices',
                manifestations: 'Note storage, Configuration, Log aggregation, CMS content'
            },
            'P21': {
                name: 'Time-Series Store',
                type: 'Pattern',
                definition: 'Time-series stores optimize storage and retrieval of timestamped data points for analytics.',
                components: 'series, timestamps, values, aggregations',
                manifestations: 'Edit history, Telemetry, Sensor data, User activity log, Stock prices'
            },
            'P22': {
                name: 'Event Bus',
                type: 'Pattern',
                definition: 'Event buses enable decoupled pub-sub communication between system components.',
                components: 'publishers, subscribers, topics, broker',
                manifestations: 'UI event system, Component communication, Plugin events, Message queues'
            },
            'P23': {
                name: 'Real-Time Sync',
                type: 'Pattern',
                definition: 'Real-time sync keeps data synchronized across multiple clients with conflict resolution.',
                components: 'local, remote, diff, merge',
                manifestations: 'Collaborative editing, Live preview, Cloud sync, Multi-device sync'
            },
            'P24': {
                name: 'Request-Response API',
                type: 'Pattern',
                definition: 'Request-response APIs provide synchronous communication with clients waiting for responses.',
                components: 'endpoints, handlers, middleware, responses',
                manifestations: 'REST API, RPC, GraphQL, Internal service APIs'
            },
            'P25': {
                name: 'Streaming Protocol',
                type: 'Pattern',
                definition: 'Streaming protocols enable continuous data flow between client and server with backpressure.',
                components: 'producer, consumer, buffer, backpressure',
                manifestations: 'WebSocket, Live updates, Progressive rendering, File uploads/downloads, Video streaming'
            },
            'P26': {
                name: 'Status Bar/Indicator',
                type: 'Pattern',
                definition: 'Status bars and indicators display system state and notifications in a persistent UI element.',
                components: 'state, measure, visualize, update',
                manifestations: 'Status Bar/Indicator in modern applications, Web-based status bar/indicator, Mobile status bar/indicator'
            },
            'P27': {
                name: 'Toast/Notification',
                type: 'Pattern',
                definition: 'Toasts and notifications display temporary messages to inform users of events and updates.',
                components: 'input, process, output, display',
                manifestations: 'Toast/Notification in modern applications, Web-based toast/notification, Mobile toast/notification'
            },
            'P28': {
                name: 'Progress Indicator',
                type: 'Pattern',
                definition: 'Progress indicators show completion status of long-running operations.',
                components: 'current, total, label, eta',
                manifestations: 'File upload/download, Build progress, Test execution, Verification progress, Installation progress'
            },
            'P29': {
                name: 'Centralized State Store',
                type: 'Pattern',
                definition: 'Centralized state stores manage application state in a single predictable container.',
                components: 'store, reducers, selectors, subscriptions',
                manifestations: 'Redux, Vuex, Global state, Application model'
            },
            'P3': {
                name: 'Hierarchical Navigator',
                type: 'Pattern',
                definition: 'Hierarchical navigators display and enable navigation through tree-structured data.',
                components: 'tree, selection, expansion, breadcrumb',
                manifestations: 'File explorer, Feature tree, Theorem library, Layer panel, Outline view'
            },
            'P30': {
                name: 'Command Pattern',
                type: 'Pattern',
                definition: 'Command pattern encapsulates requests as objects enabling undo/redo and queuing.',
                components: 'commands, executor, undo\_stack, redo\_stack',
                manifestations: 'Undo/redo system, Macro recording, Transaction log, Command history'
            },
            'P31': {
                name: 'Observer Pattern',
                type: 'Pattern',
                definition: 'Observer pattern enables objects to notify subscribers of state changes automatically.',
                components: 'subject, observers, notify',
                manifestations: 'Data binding, Event listeners, Reactive subscriptions, Pub/sub systems'
            },
            'P32': {
                name: 'Plugin Architecture',
                type: 'Pattern',
                definition: 'Plugin architecture enables dynamic extension through loadable modules with defined interfaces.',
                components: 'interface, registry, loader, lifecycle',
                manifestations: 'VS Code extensions, WordPress plugins, Browser extensions, Plugin systems'
            },
            'P33': {
                name: 'Hook System',
                type: 'Pattern',
                definition: 'Hook systems allow code injection at specific execution points for customization.',
                components: 'hooks, handlers, register, invoke',
                manifestations: 'Lifecycle hooks, Event handlers, Middleware, Aspect-oriented programming'
            },
            'P34': {
                name: 'Strategy Pattern',
                type: 'Pattern',
                definition: 'Strategy pattern encapsulates algorithms as interchangeable objects for runtime selection.',
                components: 'interface, implementations, selector, current',
                manifestations: 'File format handlers, Solver algorithms, Rendering engines, Compression algorithms'
            },
            'P4': {
                name: 'Property Inspector',
                type: 'Pattern',
                definition: 'Property inspectors display and enable editing of object properties in structured panels.',
                components: 'selection, fields, validators, commit',
                manifestations: 'Properties panel, Inspector, Settings panel, Attributes editor'
            },
            'P5': {
                name: 'Tabbed Workspace',
                type: 'Pattern',
                definition: 'Tabbed workspaces organize content into switchable tabs for efficient multi-tasking.',
                components: 'tabs, active, buffers, state',
                manifestations: 'Editor tabs, Document tabs, Multi-file editing, Chat tabs'
            },
            'P6': {
                name: 'Palette/Toolbar',
                type: 'Pattern',
                definition: 'Contextual menus provide actions relevant to the current selection or location.',
                components: 'input, process, output, display',
                manifestations: 'Palette/Toolbar in modern applications, Web-based palette/toolbar, Mobile palette/toolbar'
            },
            'P7': {
                name: 'Breadcrumb Trail',
                type: 'Pattern',
                definition: 'Dashboard layout pattern organizes information widgets in configurable grid layouts.',
                components: 'path, separators, actions',
                manifestations: 'File path, Navigation chain, Context path'
            },
            'P8': {
                name: 'Search-Based Navigation',
                type: 'Pattern',
                definition: 'Card-based layouts organize content into self-contained, reusable card components.',
                components: 'query, index, results, ranker',
                manifestations: 'File search, Theorem search, Command palette, Symbol search'
            },
            'P9': {
                name: 'Backlinks/References',
                type: 'Pattern',
                definition: 'Master-detail pattern shows list of items with detailed view of selected item.',
                components: 'input, process, output, display',
                manifestations: 'Backlinks/References in modern applications, Web-based backlinks/references, Mobile backlinks/references'
            }
        };