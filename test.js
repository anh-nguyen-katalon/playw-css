// create time tracking engines
function createEngineWithTimeTracking(engine, maxEndTime) {
  return {
    queryAll: (scope, selector) => {
      const startTime = Date.now();
      if (startTime >= maxEndTime) {
        throw new Error(`queryAll(${selector}) exceeded timeout`);
      }
      const result = engine.queryAll(scope, selector);
      const endTime = Date.now();
      if (endTime > maxEndTime) {
        throw new Error(`queryAll(${selector}) exceeded timeout`);
      }
      return result;
    }
  };
};

const originalGenerateSelector = window.katalonpw.InjectedScript.prototype.generateSelector;

// Override the generateSelector function to track start time
window.katalonpw.InjectedScript.prototype.generateSelector = function (targetElement, options) {
  // save original engines only once when generateSelector is called for the first time
  if (!this._originalEngines) {
    this._originalEngines = new Map(this._engines);
  }

  // Override the engines with time tracking engines if timeout is specified
  if (options && options.timeout) {
    // mark start time, max end time
    const timeout = options.timeout;
    const startTime = Date.now();
    const maxEndTime = startTime + timeout;

    // Override all engines with time tracking engines
    for (const [engineName, engine] of this._originalEngines) {
      this._engines.set(engineName, createEngineWithTimeTracking(engine, maxEndTime));
    }
  }
  // Restore the original engines if timeout is not specified
  else {
    for (const [engineName, engine] of this._originalEngines) {
      this._engines.set(engineName, engine);
    }
  }
  return originalGenerateSelector.call(this, targetElement, options);
};


// Initialize the injectedScript
let injectedScript = new window.katalonpw.InjectedScript(window, false, "javascript", "testId", 1, "chrome", []);


function getElementFeatures(element) {
  const features = {
    children: [],
  };
  try {
    const selector = injectedScript.generateSelector(element, { timeout: 1000 });
    if (selector && selector.includes("role")) {
      features.selector = selector;
    }
  } catch (error) {
    console.log(`Failed to generate selector for element: ${element.outerHTML} - ${error.message}`);
  }

  for (const child of element.children) {
    features.children.push(getElementFeatures(child));
  }
  return features;
}

// Get role tree of the page
function getRoleTree() {
  const bodyElem = document.querySelector("body");
  return getElementFeatures(bodyElem);
}