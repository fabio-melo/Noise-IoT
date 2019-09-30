import React from 'react';
import { Datagrid, DatagridBody, List, TextField } from 'react-admin';
import TableCell from '@material-ui/core/TableCell';
import TableRow from '@material-ui/core/TableRow';
import Checkbox from '@material-ui/core/Checkbox';

const MyDatagridRow = ({ record, resource, id, onToggleItem, children, selected, basePath }) => (
    <TableRow key={id}>
        {/* first column: selection checkbox */}
        <TableCell padding="none">
            {record.selectable && <Checkbox
                checked={selected}
                onClick={() => onToggleItem(id)}
            />}
        </TableCell>
        {/* data columns based on children */}
        {React.Children.map(children, field => (
            <TableCell key={`${id}-${field.props.source}`}>
                {React.cloneElement(field, {
                    record,
                    basePath,
                    resource,
                })}
            </TableCell>
        ))}
    </TableRow>
)

const MyDatagridBody = props => <DatagridBody {...props} row={<MyDatagridRow />} />;
export const MyDatagrid = props => <Datagrid {...props} body={<MyDatagridBody />} />;


