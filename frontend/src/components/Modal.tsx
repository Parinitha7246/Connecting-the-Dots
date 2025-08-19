import { Fragment } from 'react';

// This defines the "props" or inputs that our Modal component accepts.
interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  children: React.ReactNode;
}

// This is the reusable Modal component.
export const ConfirmationModal = ({ isOpen, onClose, onConfirm, title, children }: ModalProps) => {
  // If the modal is not supposed to be open, we render nothing.
  if (!isOpen) {
    return null;
  }

  // When the modal is open, we render the dialog.
  return (
    // We use a React Fragment to group elements without adding an extra div to the DOM.
    <Fragment>
      {/* 1. The Backdrop: A semi-transparent overlay that covers the page. */}
      {/*    Clicking it will close the modal. */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 z-40 transition-opacity"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* 2. The Modal Panel: The actual dialog box that appears in the center. */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div 
          className="bg-white rounded-lg shadow-xl w-full max-w-md mx-auto"
          role="dialog"
          aria-modal="true"
          aria-labelledby="modal-title"
        >
          {/* Modal Header and Content */}
          <div className="p-6">
            <h3 className="text-lg font-bold text-content" id="modal-title">
              {title}
            </h3>
            <div className="mt-2 text-sm text-content-subtle">
              {children}
            </div>
          </div>
          
          {/* Modal Footer with Action Buttons */}
          <div className="bg-gray-50 px-6 py-3 flex justify-end gap-3 rounded-b-lg">
            <button
              type="button"
              className="px-4 py-2 text-sm font-semibold text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
              onClick={onClose}
            >
              Cancel
            </button>
            <button
              type="button"
              className="px-4 py-2 text-sm font-semibold text-white bg-red-600 border border-transparent rounded-md shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
              onClick={onConfirm}
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </Fragment>
  );
};