const { ZodError } = require('zod');

function validateBody(schema) {
  return (req, res, next) => {
    try {
      req.body = schema.parse(req.body);
      return next();
    } catch (error) {
      if (error instanceof ZodError) {
        return res.status(400).json({ message: 'Validation failed', issues: error.issues });
      }
      return next(error);
    }
  };
}

module.exports = { validateBody };
